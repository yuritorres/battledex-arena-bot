import os
import sqlite3

SHOP_DB_PATH = os.path.join(os.path.dirname(__file__), "shop.db")
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "imagens")

# Função para conectar ao banco da loja
def create_shop_connection():
    os.makedirs(os.path.dirname(SHOP_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(SHOP_DB_PATH)
    return conn

# Função para criar tabela de itens da loja
def create_shop_table():
    conn = create_shop_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_item TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        preco INTEGER NOT NULL,
        imagem TEXT
    )''')
    conn.commit()
    conn.close()

# Função para adicionar item na loja
def add_item(id_item, nome, preco, imagem=None):
    conn = create_shop_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO itens (id_item, nome, preco, imagem) VALUES (?, ?, ?, ?)', (id_item, nome, preco, imagem))
    conn.commit()
    conn.close()

# Função para listar itens da loja
def listar_itens():
    conn = create_shop_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, id_item, nome, preco, imagem FROM itens')
    itens = cursor.fetchall()
    conn.close()
    return itens

# Função para buscar item por id
def buscar_item(item_id):
    conn = create_shop_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, id_item, nome, preco, imagem FROM itens WHERE id_item = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()
    return item

# Função para inicializar estrutura de imagens
def init_images_dir():
    os.makedirs(IMAGES_DIR, exist_ok=True)

# Inicialização automática
def init_shop():
    create_shop_table()
    init_images_dir()

init_shop()
