import os
import sqlite3
from typing import List, Tuple, Optional
from repositories.ranking_db import calcular_pontos

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
DB_PATH = os.path.join(STORAGE_DIR, "tournaments.db")


def create_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ano INTEGER,
            status TEXT DEFAULT 'draft',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tournament_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            elo INTEGER DEFAULT 1000,
            vitorias INTEGER DEFAULT 0,
            derrotas INTEGER DEFAULT 0,
            pontuacao INTEGER DEFAULT 0,
            UNIQUE(tournament_id, nome),
            FOREIGN KEY(tournament_id) REFERENCES tournaments(id)
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tournament_replays (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            jogador1 TEXT,
            jogador2 TEXT,
            score1 INTEGER,
            score2 INTEGER,
            vencedor TEXT,
            registrado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tournament_id, url),
            FOREIGN KEY(tournament_id) REFERENCES tournaments(id)
        )
        """
    )
    conn.commit()
    conn.close()


def create_tournament(nome: str, ano: Optional[int]) -> int:
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO tournaments (nome, ano, status) VALUES (?, ?, 'draft')", (nome, ano))
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return tid


def set_status(tournament_id: int, status: str) -> bool:
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("UPDATE tournaments SET status = ? WHERE id = ?", (status, tournament_id))
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def list_tournaments(limit: int = 10) -> List[Tuple]:
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, ano, status, criado_em FROM tournaments ORDER BY id DESC LIMIT ?", (limit,))
    rows = cur.fetchall()
    conn.close()
    return rows


def _ensure_player(cur, tournament_id: int, nome: str):
    cur.execute(
        "INSERT OR IGNORE INTO tournament_players (tournament_id, nome) VALUES (?, ?)",
        (tournament_id, nome),
    )


def add_player(tournament_id: int, nome: str):
    conn = create_connection()
    cur = conn.cursor()
    _ensure_player(cur, tournament_id, nome)
    conn.commit()
    conn.close()


def record_result(tournament_id: int, jogador1: str, jogador2: str, score1: int, score2: int, url: str) -> Tuple[bool, str]:
    conn = create_connection()
    cur = conn.cursor()
    # Dedup replay por campeonato
    cur.execute("SELECT 1 FROM tournament_replays WHERE tournament_id = ? AND url = ?", (tournament_id, url))
    if cur.fetchone():
        conn.close()
        return False, "⚠️ Esta batalha já foi registrada neste campeonato."

    cur.execute("SELECT status FROM tournaments WHERE id = ?", (tournament_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return False, "❌ Campeonato não encontrado."
    status = row[0]
    if status != "ativo":
        conn.close()
        return False, "❌ Campeonato não está ativo."

    vencedor = jogador1 if score1 > score2 else jogador2
    perdedor = jogador2 if vencedor == jogador1 else jogador1
    pontos = calcular_pontos(max(score1, score2), min(score1, score2))

    _ensure_player(cur, tournament_id, jogador1)
    _ensure_player(cur, tournament_id, jogador2)

    cur.execute(
        "UPDATE tournament_players SET elo = elo + ?, vitorias = vitorias + 1, pontuacao = pontuacao + ? WHERE tournament_id = ? AND nome = ?",
        (pontos, pontos, tournament_id, vencedor),
    )
    cur.execute(
        "UPDATE tournament_players SET elo = elo - ?, derrotas = derrotas + 1 WHERE tournament_id = ? AND nome = ?",
        (pontos, tournament_id, perdedor),
    )
    cur.execute(
        "INSERT INTO tournament_replays (tournament_id, url, jogador1, jogador2, score1, score2, vencedor) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (tournament_id, url, jogador1, jogador2, score1, score2, vencedor),
    )
    conn.commit()
    conn.close()
    return True, f"✅ Resultado registrado. Vencedor: {vencedor} (+{pontos})."


def ranking(tournament_id: int) -> List[Tuple]:
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT nome, elo, vitorias, derrotas, pontuacao
        FROM tournament_players
        WHERE tournament_id = ?
        ORDER BY elo DESC
        """,
        (tournament_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows
