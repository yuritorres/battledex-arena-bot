"""
BattleDex Arena - Ranking Service
Serviço compartilhado para gerenciamento de ranking ELO
"""

import os
import sqlite3
from typing import List, Tuple, Optional

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
DB_PATH = os.path.join(STORAGE_DIR, "rankingbf.db")

class RankingService:
    """Serviço para gerenciamento de ranking ELO"""
    
    @staticmethod
    def create_connection():
        """Criar conexão com banco de dados"""
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        return conn
    
    @staticmethod
    def create_table():
        """Criar tabelas do ranking"""
        conn = RankingService.create_connection()
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
    
    @staticmethod
    def add_player(nome: str) -> bool:
        """Adicionar jogador ao ranking"""
        try:
            conn = RankingService.create_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO ranking (nome) VALUES (?)", (nome,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao adicionar jogador {nome}: {e}")
            return False
    
    @staticmethod
    def remove_player(nome: str) -> bool:
        """Remover jogador do ranking"""
        try:
            conn = RankingService.create_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ranking WHERE nome = ?", (nome,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao remover jogador {nome}: {e}")
            return False
    
    @staticmethod
    def get_ranking() -> str:
        """Obter ranking formatado"""
        try:
            conn = RankingService.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT nome, elo, vitorias, derrotas FROM ranking ORDER BY elo DESC")
            rows = cursor.fetchall()
            conn.close()

            ranking_msg = "📊 Ranking BF 🔰\n\n"
            for i, row in enumerate(rows, 1):
                nome, elo, vitorias, derrotas = row
                ranking_msg += f"{i}. **{nome}** - {elo} ELO ({vitorias}V/{derrotas}D)\n"
            
            if not rows:
                ranking_msg += "Nenhum jogador no ranking ainda!"
            
            return ranking_msg
        except Exception as e:
            print(f"Erro ao obter ranking: {e}")
            return "❌ Erro ao carregar ranking!"
    
    @staticmethod
    def reset_elo(nome: str) -> bool:
        """Resetar ELO de um jogador"""
        try:
            conn = RankingService.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE ranking SET elo = 1000, vitorias = 0, derrotas = 0 WHERE nome = ?", 
                (nome,)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao resetar ELO de {nome}: {e}")
            return False
    
    @staticmethod
    def reset_all_elo() -> bool:
        """Resetar ELO de todos os jogadores"""
        try:
            conn = RankingService.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE ranking SET elo = 1000, vitorias = 0, derrotas = 0"
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao resetar todos os ELOs: {e}")
            return False
    
    @staticmethod
    def update_elo(nome: str, elo_change: int) -> bool:
        """Atualizar ELO de um jogador"""
        try:
            conn = RankingService.create_connection()
            cursor = conn.cursor()
            
            # Buscar ELO atual
            cursor.execute("SELECT elo FROM ranking WHERE nome = ?", (nome,))
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return False
            
            current_elo = result[0]
            new_elo = max(0, current_elo + elo_change)
            
            # Atualizar ELO
            cursor.execute("UPDATE ranking SET elo = ? WHERE nome = ?", (new_elo, nome))
            
            # Atualizar vitórias/derrotas
            if elo_change > 0:
                cursor.execute(
                    "UPDATE ranking SET vitorias = vitorias + 1 WHERE nome = ?", 
                    (nome,)
                )
            else:
                cursor.execute(
                    "UPDATE ranking SET derrotas = derrotas + 1 WHERE nome = ?", 
                    (nome,)
                )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao atualizar ELO de {nome}: {e}")
            return False
    
    @staticmethod
    def get_player_stats(nome: str) -> Optional[Tuple[int, int, int]]:
        """Obter estatísticas de um jogador"""
        try:
            conn = RankingService.create_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT elo, vitorias, derrotas FROM ranking WHERE nome = ?", 
                (nome,)
            )
            result = cursor.fetchone()
            conn.close()
            return result
        except Exception as e:
            print(f"Erro ao obter estatísticas de {nome}: {e}")
            return None
    
    @staticmethod
    def player_exists(nome: str) -> bool:
        """Verificar se jogador existe"""
        try:
            conn = RankingService.create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM ranking WHERE nome = ?", (nome,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            print(f"Erro ao verificar existência de {nome}: {e}")
            return False

# Inicializar tabela ao importar
RankingService.create_table()
