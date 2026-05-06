from utils.database import get_connection

conn = get_connection()
cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()

print("TABLAS EN LA BASE DE DATOS:")
for t in tables:
    print("-", t[0])

print("\nCONTENIDO DE 'games':")
try:
    rows = conn.execute("SELECT * FROM games").fetchall()
    for r in rows:
        print(dict(r))
except Exception as e:
    print("Error leyendo games:", e)

conn.close()
