"""Grounded catalogue tools used by the Campus Customs agent."""
from pathlib import Path
import json, sqlite3
from models import ProductCard
DB_PATH = Path('/Users/iin3rdyii/Desktop/data/campus_customs.db')

def search_catalogue(query: str, limit: int = 8) -> list[ProductCard]:
    normalized = query.lower().strip()
    variants = [normalized, normalized[:-1] if normalized.endswith('s') else normalized]
    terms = [f'%{variant}%' for variant in variants for _ in range(4)]
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute('''SELECT c.*, i.size, i.quantity FROM catalogue c LEFT JOIN inventory i ON i.product_id=c.product_id WHERE (lower(c.garment_type) LIKE ? OR lower(c.description) LIKE ? OR lower(c.name) LIKE ? OR lower(c.search_tags) LIKE ?) OR (lower(c.garment_type) LIKE ? OR lower(c.description) LIKE ? OR lower(c.name) LIKE ? OR lower(c.search_tags) LIKE ?) ORDER BY c.name LIMIT ?''', (*terms, limit * 20)).fetchall()
    grouped = {}
    for row in rows:
        p = grouped.setdefault(row['product_id'], ProductCard(product_id=row['product_id'], name=row['name'], garment_type=row['garment_type'], description=row['description'], price=row['price'], image_file_path=row['image_file_path'], colors=json.loads(row['colors']), inventory=[]))
        if row['size'] is not None: p.inventory.append({'size': row['size'], 'quantity': row['quantity']})
    for p in grouped.values(): p.total_stock = sum(i['quantity'] for i in p.inventory)
    return list(grouped.values())[:limit]

def get_product_details(product_id: str) -> ProductCard | None:
    """Return one catalogue record and every size quantity for an exact product ID."""
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        row = db.execute('SELECT * FROM catalogue WHERE product_id = ?', (product_id,)).fetchone()
        if not row: return None
        stock = db.execute('SELECT size, quantity FROM inventory WHERE product_id = ? ORDER BY size', (product_id,)).fetchall()
    p = ProductCard(product_id=row['product_id'], name=row['name'], garment_type=row['garment_type'], description=row['description'], price=row['price'], image_file_path=row['image_file_path'], colors=json.loads(row['colors']), inventory=[{'size': r['size'], 'quantity': r['quantity']} for r in stock])
    p.total_stock = sum(r.quantity for r in p.inventory)
    return p

def check_stock(product_id: str) -> dict:
    """Read current inventory for an exact product ID; zero quantities mean out of stock."""
    product = get_product_details(product_id)
    if product is None: return {'product_id': product_id, 'found': False, 'in_stock': False, 'total_stock': 0, 'inventory': []}
    return {'product_id': product_id, 'found': True, 'in_stock': product.total_stock > 0, 'total_stock': product.total_stock, 'inventory': [r.model_dump() for r in product.inventory]}
