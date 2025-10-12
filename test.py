import sqlite3

conn = sqlite3.connect("coral_tech.db")
cursor = conn.cursor()
cursor.execute("SELECT id_rubro, nombre_rubro FROM rubro;")
print(cursor.fetchall())
conn.close()
