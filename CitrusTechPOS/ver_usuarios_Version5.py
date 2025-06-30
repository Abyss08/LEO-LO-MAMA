import sqlite3

DB_NAME = "citrus_tech.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Muestra la estructura de la tabla
print("Estructura de la tabla usuarios:")
cursor.execute("PRAGMA table_info(usuarios)")
for col in cursor.fetchall():
    print(col)

# Muestra todos los registros
print("\nUsuarios en la base de datos:")
try:
    cursor.execute("SELECT * FROM usuarios")
    for row in cursor.fetchall():
        print(row)
except Exception as e:
    print("Error al leer usuarios:", e)

conn.close()