import sqlite3

DB_NAME = "citrus_tech.db"

def print_table_info(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(productos);")
    columns = cursor.fetchall()
    print("Estructura actual de la tabla productos:")
    for col in columns:
        print(col)
    print("-" * 40)

def tabla_tiene_id_producto(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(productos);")
    columns = cursor.fetchall()
    return any(col[1] == "id_producto" for col in columns)

def migrar_tabla(conn):
    cursor = conn.cursor()
    print("Migrando datos...")

    # Renombrar la tabla original
    cursor.execute("ALTER TABLE productos RENAME TO productos_old;")

    # Crear la nueva tabla con el esquema correcto
    cursor.execute('''
        CREATE TABLE productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio_venta REAL NOT NULL,
            stock INTEGER NOT NULL
        );
    ''')

    # Intentar migrar los datos antiguos (sin id_producto, dejando que SQLite lo genere automáticamente)
    cursor.execute("SELECT sku, nombre, descripcion, precio_venta, stock FROM productos_old;")
    for row in cursor.fetchall():
        cursor.execute("""
            INSERT INTO productos (sku, nombre, descripcion, precio_venta, stock)
            VALUES (?, ?, ?, ?, ?)
        """, row)

    # Borrar la tabla antigua
    cursor.execute("DROP TABLE productos_old;")
    conn.commit()
    print("Migración completada.")

def main():
    conn = sqlite3.connect(DB_NAME)
    print_table_info(conn)
    if tabla_tiene_id_producto(conn):
        print("La tabla 'productos' YA tiene la columna 'id_producto'. No se requiere acción.")
    else:
        print("La tabla 'productos' NO tiene la columna 'id_producto'. Se migrará la estructura...")
        migrar_tabla(conn)
        print_table_info(conn)
        print("La tabla 'productos' ha sido actualizada correctamente.")
    conn.close()

if __name__ == "__main__":
    main()