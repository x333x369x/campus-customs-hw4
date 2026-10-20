"""Campus Customs API: catalogue search plus hardened account registration/login."""
from pathlib import Path
import base64, hashlib, hmac, os, re, secrets, sqlite3
from cryptography.fernet import Fernet, InvalidToken
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field, field_validator

DB_PATH = Path('/Users/iin3rdyii/Desktop/data/campus_customs.db')
ITERATIONS = 120_000
KEY = os.getenv('CAMPUS_CUSTOMS_ENCRYPTION_KEY')
if not KEY:
    # Development fallback only; production must provide a persistent secret.
    KEY = base64.urlsafe_b64encode(hashlib.sha256(b'development-only-change-me').digest()).decode()
CIPHER = Fernet(KEY)
app = FastAPI(title='Campus Customs API')
app.add_middleware(CORSMiddleware, allow_origins=['http://localhost:5173'], allow_methods=['*'], allow_headers=['*'])

def connection():
    db = sqlite3.connect(DB_PATH); db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON'); return db

def migrate_users():
    with connection() as db:
        cols = {r['name'] for r in db.execute('PRAGMA table_info(users)')}
        if 'email_ciphertext' not in cols: db.execute('ALTER TABLE users ADD COLUMN email_ciphertext TEXT')
        if 'email_lookup' not in cols: db.execute('ALTER TABLE users ADD COLUMN email_lookup TEXT')
        db.execute('CREATE UNIQUE INDEX IF NOT EXISTS users_email_lookup ON users(email_lookup)')
migrate_users()

def search_products(q: str):
    terms = [f'%{q.lower()}%'] * 4
    with connection() as db:
        rows = db.execute('''SELECT c.*, i.size, i.quantity FROM catalogue c LEFT JOIN inventory i ON i.product_id=c.product_id WHERE lower(c.garment_type) LIKE ? OR lower(c.description) LIKE ? OR lower(c.name) LIKE ? OR lower(c.search_tags) LIKE ? ORDER BY c.name''', terms).fetchall()
    products = {}
    for r in rows:
        p = products.setdefault(r['product_id'], {k:r[k] for k in ['product_id','name','garment_type','description','colors','search_tags','image_file_path','price']} | {'inventory': []})
        if r['size'] is not None: p['inventory'].append({'size':r['size'],'quantity':r['quantity']})
    return list(products.values())

@app.get('/api/products')
def products(q: str = Query('', max_length=100)): return {'products': search_products(q or 'Yale')}

class Register(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    confirm_password: str
    @field_validator('first_name','last_name')
    @classmethod
    def safe_name(cls, value):
        if not re.fullmatch(r"[A-Za-zÀ-ÿ' -]+", value): raise ValueError('Name contains invalid characters')
        return value.strip()
    def validate_password(self):
        p=self.password
        if p != self.confirm_password or not (re.search(r'[A-Z]',p) and re.search(r'[a-z]',p) and re.search(r'\d',p) and re.search(r'[^A-Za-z0-9]',p)):
            raise ValueError('Password must match confirmation and contain upper, lower, number, and special character')

def password_record(password):
    salt=secrets.token_bytes(16)
    digest=hashlib.pbkdf2_hmac('sha256', password.encode(), salt, ITERATIONS)
    return base64.b64encode(salt).decode(), base64.b64encode(digest).decode()
def valid_password(password, salt, digest):
    check=hashlib.pbkdf2_hmac('sha256', password.encode(), base64.b64decode(salt), ITERATIONS)
    return hmac.compare_digest(check, base64.b64decode(digest))
def lookup_email(email): return hmac.new(KEY.encode(), email.strip().lower().encode(), hashlib.sha256).hexdigest()

@app.post('/api/auth/register')
def register(body: Register):
    try: body.validate_password()
    except ValueError as e: raise HTTPException(422, str(e))
    email=body.email.lower(); lookup=lookup_email(email); salt,digest=password_record(body.password)
    with connection() as db:
        try:
            db.execute('INSERT INTO users (name,email,password_hash,first_name,last_name,email_ciphertext,email_lookup) VALUES (?,?,?,?,?,?,?)', (CIPHER.encrypt((body.first_name+' '+body.last_name).encode()).decode(), CIPHER.encrypt(email.encode()).decode(), f'pbkdf2_sha256${ITERATIONS}${salt}${digest}', CIPHER.encrypt(body.first_name.encode()).decode(), CIPHER.encrypt(body.last_name.encode()).decode(), CIPHER.encrypt(email.encode()).decode(), lookup)); db.commit()
        except sqlite3.IntegrityError: raise HTTPException(409, 'An account with that email already exists')
    return {'message':'Account created'}

class Login(BaseModel): email: EmailStr; password: str
@app.post('/api/auth/login')
def login(body: Login):
    with connection() as db: row=db.execute('SELECT id,password_hash FROM users WHERE email_lookup=?', (lookup_email(body.email),)).fetchone()
    if not row: raise HTTPException(401, 'Invalid email or password')
    try: _,iterations,salt,digest=row['password_hash'].split('$')
    except ValueError: raise HTTPException(401, 'Invalid email or password')
    if int(iterations)!=ITERATIONS or not valid_password(body.password,salt,digest): raise HTTPException(401, 'Invalid email or password')
    return {'message':'Signed in','user_id':row['id']}

@app.get('/api/health')
def health(): return {'status':'ok','service':'campus-customs'}
