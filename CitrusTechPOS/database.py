import sqlite3
import hashlib
import json
from datetime import datetime

DB_NAME = 'citrus_tech.db'

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_usuario TEXT UNIQUE NOT NULL,
        clave TEXT NOT NULL,
        privilegio TEXT NOT NULL CHECK(privilegio IN ('admin', 'vendedor'))
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        sku TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        precio_venta REAL NOT NULL,
        stock INTEGER NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
        id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TIMESTAMP NOT NULL,
        id_usuario INTEGER,
        total REAL NOT NULL,
        detalles TEXT NOT NULL,
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
    )''')

    cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = 'admin'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO usuarios (nombre_usuario, clave, privilegio) VALUES (?, ?, ?)",
                       ('admin', hash_password('admin123'), 'admin'))

    cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = 'vendedor1'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO usuarios (nombre_usuario, clave, privilegio) VALUES (?, ?, ?)",
                       ('vendedor1', hash_password('venta123'), 'vendedor'))

    conn.commit()
    conn.close()

def verificar_usuario(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_usuario, privilegio FROM usuarios WHERE nombre_usuario = ? AND clave = ?",
                   (username, hash_password(password)))
    user = cursor.fetchone()
    conn.close()
    return user

def agregar_producto(sku, nombre, descripcion, precio, stock):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO productos (sku, nombre, descripcion, precio_venta, stock) VALUES (?, ?, ?, ?, ?)",
                       (sku, nombre, descripcion, precio, stock))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def obtener_productos(query=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if query:
        cursor.execute("SELECT * FROM productos WHERE nombre LIKE ? OR sku LIKE ?", ('%'+query+'%', '%'+query+'%'))
    else:
        cursor.execute("SELECT * FROM productos ORDER BY nombre ASC")
    productos = cursor.fetchall()
    conn.close()
    return productos

def actualizar_producto(sku, nombre, descripcion, precio, stock):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET nombre = ?, descripcion = ?, precio_venta = ?, stock = ? WHERE sku = ?", 
                   (nombre, descripcion, precio, stock, sku))
    conn.commit()
    conn.close()

def eliminar_producto(sku):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE sku = ?", (sku,))
    conn.commit()
    conn.close()

def registrar_venta(id_usuario, total, detalles_lista):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    detalles_json = json.dumps(detalles_lista)
    cursor.execute("INSERT INTO ventas (fecha, id_usuario, total, detalles) VALUES (?, ?, ?, ?)",
                   (datetime.now(), id_usuario, total, detalles_json))

    for item in detalles_lista:
        cursor.execute("UPDATE productos SET stock = stock - ? WHERE sku = ?", (item['cantidad'], item['sku']))

    conn.commit()
    conn.close()

def obtener_ventas_por_fecha(fecha_inicio, fecha_fin):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = '''
    SELECT v.id_venta, v.fecha, u.nombre_usuario, v.total, v.detalles
    FROM ventas v
    JOIN usuarios u ON v.id_usuario = u.id
    WHERE date(v.fecha) BETWEEN ? AND ?
    ORDER BY v.fecha DESC
    '''
    cursor.execute(query, (fecha_inicio, fecha_fin))
    ventas = cursor.fetchall()
    conn.close()
    return ventas