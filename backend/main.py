"""Run from backend/: uvicorn main:app --reload --port 8000"""
from pathlib import Path
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from agent import agent
from models import ChatRequest, ChatReply, ChatDeps, PageContext
load_dotenv(Path(__file__).parents[1] / '.env')
DB=Path('/Users/iin3rdyii/Desktop/data/campus_customs.db')
AUDIT=Path(__file__).parents[1] / 'output' / 'audit_trail.json'
AUDIT.parent.mkdir(parents=True, exist_ok=True)
if not AUDIT.exists(): AUDIT.touch()

def audit(event):
    # JSON Lines keeps every event append-only; never truncate or rewrite this file.
    with AUDIT.open('a', encoding='utf-8') as f:
        f.write(json.dumps(event, separators=(',', ':')) + '\n')
app=FastAPI(title='Campus Customs Chat API')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173'],allow_methods=['*'],allow_headers=['*'])

def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
class Request(ChatRequest):
 user_id: int|None=None
 page_context: PageContext=PageContext()

@app.post('/api/chat',response_model=ChatReply)
async def chat(request: Request):
    # Guests get no history and their supplied user ID is never trusted without a server-side account check.
    uid=request.user_id
    history=[]
    name=email=None
    with db() as c:
        if uid is not None and c.execute('SELECT 1 FROM users WHERE id=?',(uid,)).fetchone():
            rows=c.execute("SELECT role,content FROM chat_messages WHERE user_id=? ORDER BY id DESC LIMIT 20",(uid,)).fetchall()
            history=[{'role':r['role'],'content':r['content']} for r in reversed(rows)]
            name=f'Campus Customs customer {uid}'
    deps=ChatDeps(user_id=uid if name else None,customer_name=name,customer_email=email,page_context=request.page_context)
    context=f"Page context: {request.page_context.model_dump_json()}. Customer: {name or 'guest (no memory)'}."
    request_id=str(uuid.uuid4())
    try:
        result=await agent.run(context+'\nShopper message: '+request.message,deps=deps)
    except Exception as exc:
        audit({'timestamp':datetime.now(timezone.utc).isoformat(),'request_id':request_id,'customer_type':'authenticated' if name else 'guest','status':'error','products_returned':0,'stop_reason':'agent_error'})
        raise HTTPException(502,'The shopping assistant is temporarily unavailable.') from exc
    audit({'timestamp':datetime.now(timezone.utc).isoformat(),'request_id':request_id,'customer_type':'authenticated' if name else 'guest','status':'completed','products_returned':len(result.output.products),'stop_reason':'completed'})
    if name:
        with db() as c:
            c.execute('INSERT INTO chat_messages (user_id,role,content,products_json) VALUES (?,?,?,?)',(uid,'user',request.message,None))
            c.execute('INSERT INTO chat_messages (user_id,role,content,products_json) VALUES (?,?,?,?)',(uid,'assistant',result.output.reply,result.output.model_dump_json()))
            c.commit()
    return result.output
@app.get('/api/health')
def health(): return {'status':'ok','service':'campus-customs-chat'}

# Serve the production React build from the same process as the API.
STATIC_DIR = Path(__file__).parent / 'static'
if STATIC_DIR.exists():
    app.mount('/', StaticFiles(directory=STATIC_DIR, html=True), name='frontend')
