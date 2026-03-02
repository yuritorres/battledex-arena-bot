import os
import sqlite3

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
COINS_DB_PATH = os.path.join(STORAGE_DIR, "coins.db")

# Função para conectar ao novo banco
def create_coins_connection():
    os.makedirs(os.path.dirname(COINS_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(COINS_DB_PATH)
    return conn

# Função para criar tabela de moedas
def create_coins_table():
    conn = create_coins_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS coins (
        nome TEXT PRIMARY KEY,
        moedas INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

# Função para adicionar moedas ao jogador
def add_coins(nome, quantidade):
    conn = create_coins_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO coins (nome, moedas) VALUES (?, 0)', (nome,))
    cursor.execute('UPDATE coins SET moedas = moedas + ? WHERE nome = ?', (quantidade, nome))
    conn.commit()
    conn.close()

# Função para consultar saldo de moedas
def get_coins(nome):
    conn = create_coins_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT moedas FROM coins WHERE nome = ?', (nome,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

# Função para remover moedas
def remove_coins(nome, quantidade):
    conn = create_coins_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE coins SET moedas = moedas - ? WHERE nome = ?', (quantidade, nome))
    conn.commit()
    conn.close()

# Função para ranking de moedas
def coins_leaderboard():
    conn = create_coins_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT nome, moedas FROM coins ORDER BY moedas DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Inicialização automática da tabela ao importar
create_coins_table()
