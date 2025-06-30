import sqlite3
import random
import string

DB_NAME = "citrus_tech.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()
    # SOLO crea la tabla usuarios si no existe, NO la borra ni la modifica si ya existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            nombre TEXT
        );
    """)
    # Crea tabla productos si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
            sku TEXT UNIQUE,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio_venta REAL NOT NULL,
            stock INTEGER NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def verificar_usuario(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, username, nombre FROM usuarios WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {
            "id_usuario": user[0],
            "username": user[1],
            "nombre": user[2] if user[2] else ""
        }
    else:
        return None

def generar_sku(longitud=8):
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choices(caracteres, k=longitud))

def insertar_producto(nombre, descripcion, precio_venta, stock):
    conn = get_connection()
    cursor = conn.cursor()
    intentos = 0
    max_intentos = 10
    while intentos < max_intentos:
        sku = generar_sku()
        try:
            cursor.execute("""
                INSERT INTO productos (sku, nombre, descripcion, precio_venta, stock)
                VALUES (?, ?, ?, ?, ?)
            """, (sku, nombre, descripcion, float(precio_venta), int(stock)))
            conn.commit()
            print(f"Producto insertado con SKU: {sku}")
            break
        except sqlite3.IntegrityError:
            intentos += 1
    else:
        print("No se pudo generar un SKU único después de varios intentos.")
    conn.close()

def obtener_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id_producto, sku, nombre, descripcion, precio_venta, stock
        FROM productos
        ORDER BY nombre ASC
    """)
    productos = cursor.fetchall()
    conn.close()
    return productos

# Este bloque solo es para pruebas, puedes quitarlo si no lo necesitas
if __name__ == "__main__":
    setup_database()
    print("\nProductos actuales:")
    for p in obtener_productos():
        print(p)