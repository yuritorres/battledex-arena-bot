import sqlite3
import os

INVENTARIO_DB_PATH = os.path.join(os.path.dirname(__file__), "inventario.db")

def create_inventario_connection():
    os.makedirs(os.path.dirname(INVENTARIO_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(INVENTARIO_DB_PATH)
    return conn

def create_inventario_table():
    conn = create_inventario_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT NOT NULL,
        id_item TEXT NOT NULL,
        quantidade INTEGER DEFAULT 1,
        UNIQUE(usuario, id_item)
    )''')
    conn.commit()
    conn.close()

def adicionar_ao_inventario(usuario, id_item, quantidade=1):
    conn = create_inventario_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT quantidade FROM inventario WHERE usuario = ? AND id_item = ?', (usuario, id_item))
    row = cursor.fetchone()
    if row:
        cursor.execute('UPDATE inventario SET quantidade = quantidade + ? WHERE usuario = ? AND id_item = ?', (quantidade, usuario, id_item))
    else:
        cursor.execute('INSERT INTO inventario (usuario, id_item, quantidade) VALUES (?, ?, ?)', (usuario, id_item, quantidade))
    conn.commit()
    conn.close()

def listar_inventario(usuario):
    conn = create_inventario_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id_item, quantidade FROM inventario WHERE usuario = ?', (usuario,))
    itens = cursor.fetchall()
    conn.close()
    return itens

def init_inventario():
    create_inventario_table()

init_inventario()
