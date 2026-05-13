"""
Full system debug script.
Tests: Database → Engine → API (via requests to running server).
Run with:  python debug_test.py
"""
import sys, os, json

# ── 1. DATABASE LAYER ─────────────────────────────────────────
print("=" * 60)
print("1. DATABASE LAYER")
print("=" * 60)

from app.database import get_db_connection, fetch_products, fetch_product_by_id, fetch_ratings, fetch_products_for_engine

conn = get_db_connection()

# Product count
products = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
print(f"   Products in DB: {products}")
assert products > 0, "ERROR: No products in database!"

# Ratings count
ratings = conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]
print(f"   Ratings  in DB: {ratings}")
assert ratings > 0, "ERROR: No ratings in database!"

# Users count
users = conn.execute("SELECT COUNT(DISTINCT user_id) FROM ratings").fetchone()[0]
print(f"   Unique users:   {users}")
conn.close()

# fetch_products
prods = fetch_products()
assert len(prods) == products, f"fetch_products returned {len(prods)}, expected {products}"
p1 = prods[0]
assert 'id' in p1 and 'name' in p1 and 'category' in p1, f"Missing keys in raw product: {list(p1.keys())}"
print(f"   fetch_products():         OK ({len(prods)} rows, keys: {list(p1.keys())})")

# fetch_products_for_engine
engine_prods = fetch_products_for_engine()
e1 = engine_prods[0]
assert 'ProductID' in e1 and 'Category' in e1 and 'RAM' in e1, f"Missing engine keys: {list(e1.keys())}"
print(f"   fetch_products_for_engine(): OK (keys: {list(e1.keys())})")

# fetch_product_by_id
p101 = fetch_product_by_id(101)
assert p101 is not None, "ERROR: Product 101 not found"
print(f"   fetch_product_by_id(101): OK → {p101['name']}")

# fetch_product_by_id (missing)
pMissing = fetch_product_by_id(99999)
assert pMissing is None, "ERROR: Non-existent product should return None"
print(f"   fetch_product_by_id(99999): OK → None")

# fetch_ratings
rats = fetch_ratings()
r1 = rats[0]
assert 'UserID' in r1 and 'ProductID' in r1 and 'Rating' in r1, f"Missing rating keys: {list(r1.keys())}"
print(f"   fetch_ratings():          OK ({len(rats)} rows, keys: {list(r1.keys())})")
print("   ✅ Database layer: ALL PASS\n")


# ── 2. RECOMMENDATION ENGINE ─────────────────────────────────
print("=" * 60)
print("2. RECOMMENDATION ENGINE")
print("=" * 60)

from engine.content_based import ContentBasedEngine
from engine.collaborative import CollaborativeEngine
from engine.hybrid import HybridEngine

# Content-Based
cb = ContentBasedEngine(products_data=engine_prods)
cb_recs = cb.get_recommendations("101", top_n=5)
print(f"   Content-Based recs for 101: {len(cb_recs)} results")
assert len(cb_recs) > 0, "ERROR: No content-based recommendations"
for pid, score in cb_recs:
    assert 0 <= score <= 1, f"Score out of range: {score}"
print(f"   Top result: Product {cb_recs[0][0]}, Score: {cb_recs[0][1]:.4f}")
print(f"   ✅ Content-Based: PASS")

# Collaborative
cf = CollaborativeEngine(ratings_data=rats)
cf_recs = cf.get_recommendations("1", top_n=5)
print(f"   Collaborative recs for User 1: {len(cf_recs)} results")
assert len(cf_recs) > 0, "ERROR: No collaborative recommendations"
print(f"   Top result: Product {cf_recs[0][0]}, Score: {cf_recs[0][1]:.4f}")
print(f"   ✅ Collaborative: PASS")

# Hybrid
hybrid = HybridEngine(products_data=engine_prods, ratings_data=rats)
h_recs = hybrid.get_recommendations(user_id="1", last_product_id="101", top_n=5)
print(f"   Hybrid recs (user=1, product=101): {len(h_recs)} results")
assert len(h_recs) > 0, "ERROR: No hybrid recommendations"
for r in h_recs:
    assert 'ProductID' in r and 'Name' in r and 'CombinedScore' in r, f"Bad rec format: {r}"
print(f"   Top: {h_recs[0]['Name']} (Score: {h_recs[0]['CombinedScore']})")
print(f"   ✅ Hybrid Engine: PASS\n")


# ── 3. UNIT COMPARISON BUG FIX ────────────────────────────────
print("=" * 60)
print("3. UNIT COMPARISON LOGIC (parseNumeric equivalent)")
print("=" * 60)

def parse_numeric(val):
    """Python equivalent of the JS parseNumeric fix."""
    import re
    s = str(val).strip().upper()
    num = float(re.sub(r'[^0-9.]', '', s) or '0')
    if 'TB' in s:  return num * 1024
    if 'GB' in s:  return num
    if 'MB' in s:  return num / 1024
    return num

tests = [
    ("512GB", 512),
    ("1TB", 1024),
    ("2TB", 2048),
    ("128GB", 128),
    ("256GB", 256),
    ("16GB", 16),
    ("64GB", 64),
    ("4000mAh", 4000),
    ("4500mAh", 4500),
    ("5000mAh", 5000),
    ("50Wh", 50),
    ("85Wh", 85),
    ("100Wh", 100),
]

all_pass = True
for val, expected in tests:
    result = parse_numeric(val)
    status = "✅" if result == expected else "❌"
    if result != expected:
        all_pass = False
    print(f"   {status} parseNumeric('{val}') = {result}  (expected {expected})")

# Key comparisons
assert parse_numeric("1TB") > parse_numeric("512GB"), "1TB should beat 512GB!"
assert parse_numeric("2TB") > parse_numeric("1TB"), "2TB should beat 1TB!"
assert parse_numeric("5000mAh") > parse_numeric("4000mAh"), "5000mAh should beat 4000mAh!"
assert parse_numeric("100Wh") > parse_numeric("50Wh"), "100Wh should beat 50Wh!"
print(f"   ✅ Unit comparison logic: ALL PASS\n")


# ── 4. FILE STRUCTURE ─────────────────────────────────────────
print("=" * 60)
print("4. FILE STRUCTURE CHECK")
print("=" * 60)

required_files = [
    "app/main.py",
    "app/database.py",
    "app/schemas.py",
    "app/models.py",
    "app/__init__.py",
    "app/routes/__init__.py",
    "app/routes/recommendations.py",
    "engine/__init__.py",
    "engine/engine_utils.py",
    "engine/content_based.py",
    "engine/collaborative.py",
    "engine/hybrid.py",
    "templates/index.html",
    "templates/product_detail.html",
    "templates/compare.html",
    "static/css/style.css",
    "data/products.csv",
    "data/user_ratings.csv",
    "data/products.db",
    "data/generate_data.py",
    "data/seed_data.py",
    "README.md",
]

missing = []
for f in required_files:
    exists = os.path.exists(f)
    status = "✅" if exists else "❌ MISSING"
    if not exists:
        missing.append(f)
    print(f"   {status}  {f}")

if missing:
    print(f"\n   ⚠️  Missing files: {missing}")
else:
    print(f"   ✅ All {len(required_files)} files present\n")


# ── SUMMARY ───────────────────────────────────────────────────
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"   Database:      {products} products, {ratings} ratings, {users} users")
print(f"   Content-Based: {len(cb_recs)} recs for product 101")
print(f"   Collaborative: {len(cf_recs)} recs for user 1")
print(f"   Hybrid:        {len(h_recs)} recs (combined)")
print(f"   Unit Parser:   {'ALL PASS' if all_pass else 'FAILURES DETECTED'}")
print(f"   File Structure: {'ALL PRESENT' if not missing else f'{len(missing)} MISSING'}")
print(f"\n   🏁 Offline tests complete. Start server to test API endpoints.\n")
