import os
import sqlite3

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "storage"))
DB_PATH = os.path.join(STORAGE_DIR, "rankingbf.db")

def create_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ranking (
        nome TEXT PRIMARY KEY,
        elo INTEGER DEFAULT 1000,
        vitorias INTEGER DEFAULT 0,
        derrotas INTEGER DEFAULT 0
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS replays (
        url TEXT PRIMARY KEY
    )''')
    conn.commit()
    conn.close()

def add_player(nome):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO ranking (nome) VALUES (?)", (nome,))
    conn.commit()
    conn.close()

def remove_player(nome):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ranking WHERE nome = ?", (nome,))
    conn.commit()
    conn.close()

def get_ranking():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, elo, vitorias, derrotas FROM ranking ORDER BY elo DESC")
    rows = cursor.fetchall()
    conn.close()

    ranking_msg = "📊 Ranking BF 🔰\n\n"
    for i, row in enumerate(rows, 1):
        medal = "⭐️" if i == 1 else f"{i}."
        ranking_msg += f"{medal} {row[0]} - Elo: {row[1]} | 🟢 {row[2]} / 🔴 {row[3]}\n"
    return ranking_msg if rows else "Nenhum jogador no ranking."

def update_elo(vencedor, perdedor, pontos, link):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE ranking SET elo = elo + ?, vitorias = vitorias + 1 WHERE nome = ?", (pontos, vencedor))
    cursor.execute(
        "UPDATE ranking SET elo = elo - ?, derrotas = derrotas + 1 WHERE nome = ?", (pontos, perdedor))
    cursor.execute("INSERT OR IGNORE INTO replays (url) VALUES (?)", (link,))
    cursor.execute("SELECT elo FROM ranking WHERE nome = ?", (vencedor,))
    elo_vencedor = cursor.fetchone()[0]
    cursor.execute("SELECT elo FROM ranking WHERE nome = ?", (perdedor,))
    elo_perdedor = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return elo_vencedor, elo_perdedor

def calcular_pontos(score_vencedor, score_perdedor):
    diferenca = score_vencedor - score_perdedor
    if diferenca >= 6:
        return 30
    elif diferenca == 5:
        return 20
    elif diferenca == 4:
        return 15
    elif diferenca == 3:
        return 12
    else:
        return 10
