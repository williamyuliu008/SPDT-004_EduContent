import sqlite3, json, os

DB_PATH = r"D:\92_products\SPDT-001_Harmony\_03_knowledge\mmc_archive.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Initialize schema (idempotent)
c.execute("CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, app_name TEXT NOT NULL, brand TEXT NOT NULL, version TEXT DEFAULT 'V1.0', created_at TEXT NOT NULL, metadata_json TEXT, source_dir TEXT, tags TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS depgraph (id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, target TEXT NOT NULL, relation TEXT NOT NULL, description TEXT, created_at TEXT NOT NULL)")
c.execute("CREATE TABLE IF NOT EXISTS brands (id INTEGER PRIMARY KEY AUTOINCREMENT, brand_name TEXT UNIQUE NOT NULL, primary_color TEXT NOT NULL, positioning TEXT, app_count INTEGER DEFAULT 0, created_at TEXT NOT NULL)")

# Clear old data
c.execute("DELETE FROM events")
c.execute("DELETE FROM depgraph")
c.execute("DELETE FROM brands")

conn.commit()
print("DB schema ready")
conn.close()
