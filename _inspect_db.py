import sqlite3
conn = sqlite3.connect(r'c:\Users\jola-\OneDrive\Dokumenty\GitHub\SOKs_LOK\Database_Files\Database.db')
cursor = conn.cursor()
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
for r in cursor.fetchall():
    print(r[0], ':', r[1])
print('---')
cursor.execute("SELECT * FROM konkurencje_lista")
for r in cursor.fetchall():
    print(r)
conn.close()
