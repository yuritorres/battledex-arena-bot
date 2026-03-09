"""
BattleDex Arena - Coins Service
Serviço compartilhado para gerenciamento de moedas
"""

import os
import sqlite3
from typing import List, Tuple, Optional

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
COINS_DB_PATH = os.path.join(STORAGE_DIR, "coins.db")

class CoinsService:
    """Serviço para gerenciamento de moedas"""
    
    @staticmethod
    def create_connection():
        """Criar conexão com banco de dados"""
        os.makedirs(os.path.dirname(COINS_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(COINS_DB_PATH)
        return conn
    
    @staticmethod
    def create_table():
        """Criar tabela de moedas"""
        conn = CoinsService.create_connection()
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS coins (
            nome TEXT PRIMARY KEY,
            moedas INTEGER DEFAULT 0
        )''')
        conn.commit()
        conn.close()
    
    @staticmethod
    def add_coins(nome: str, quantidade: int) -> bool:
        """Adicionar moedas ao jogador"""
        try:
            if quantidade <= 0:
                return False
                
            conn = CoinsService.create_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO coins (nome, moedas) VALUES (?, 0)', (nome,))
            cursor.execute('UPDATE coins SET moedas = moedas + ? WHERE nome = ?', (quantidade, nome))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao adicionar moedas para {nome}: {e}")
            return False
    
    @staticmethod
    def get_balance(nome: str) -> int:
        """Consultar saldo de moedas"""
        try:
            conn = CoinsService.create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT moedas FROM coins WHERE nome = ?', (nome,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else 0
        except Exception as e:
            print(f"Erro ao consultar saldo de {nome}: {e}")
            return 0
    
    @staticmethod
    def remove_coins(nome: str, quantidade: int) -> bool:
        """Remover moedas do jogador"""
        try:
            if quantidade <= 0:
                return False
                
            conn = CoinsService.create_connection()
            cursor = conn.cursor()
            
            # Verificar saldo atual
            cursor.execute('SELECT moedas FROM coins WHERE nome = ?', (nome,))
            row = cursor.fetchone()
            
            if not row or row[0] < quantidade:
                conn.close()
                return False
            
            cursor.execute('UPDATE coins SET moedas = moedas - ? WHERE nome = ?', (quantidade, nome))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao remover moedas de {nome}: {e}")
            return False
    
    @staticmethod
    def get_coins_ranking() -> str:
        """Obter ranking de moedas formatado"""
        try:
            conn = CoinsService.create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nome, moedas FROM coins ORDER BY moedas DESC")
            rows = cursor.fetchall()
            conn.close()

            ranking_msg = "💰 Ranking de Coins 💰\n\n"
            for i, row in enumerate(rows, 1):
                nome, moedas = row
                ranking_msg += f"{i}. **{nome}** - {moedas} coins\n"
            
            if not rows:
                ranking_msg += "Nenhum jogador com coins ainda!"
            
            return ranking_msg
        except Exception as e:
            print(f"Erro ao obter ranking de coins: {e}")
            return "❌ Erro ao carregar ranking de coins!"
    
    @staticmethod
    def penalize_player(nome: str, quantidade: int) -> bool:
        """Penalizar jogador removendo moedas"""
        return CoinsService.remove_coins(nome, quantidade)
    
    @staticmethod
    def transfer_coins(from_user: str, to_user: str, quantidade: int) -> bool:
        """Transferir moedas entre jogadores"""
        try:
            if quantidade <= 0:
                return False
            
            conn = CoinsService.create_connection()
            cursor = conn.cursor()
            
            # Verificar saldo do remetente
            cursor.execute('SELECT moedas FROM coins WHERE nome = ?', (from_user,))
            from_row = cursor.fetchone()
            
            if not from_row or from_row[0] < quantidade:
                conn.close()
                return False
            
            # Realizar transferência
            cursor.execute('UPDATE coins SET moedas = moedas - ? WHERE nome = ?', (quantidade, from_user))
            cursor.execute('INSERT OR IGNORE INTO coins (nome, moedas) VALUES (?, 0)', (to_user,))
            cursor.execute('UPDATE coins SET moedas = moedas + ? WHERE nome = ?', (quantidade, to_user))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro na transferência de {from_user} para {to_user}: {e}")
            return False
    
    @staticmethod
    def get_top_balance(limit: int = 10) -> List[Tuple[str, int]]:
        """Obter top jogadores por saldo (compatibilidade com Discord)"""
        return CoinsService.get_top_players(limit)
    
    @staticmethod
    def get_top_players(limit: int = 10) -> List[Tuple[str, int]]:
        """Obter top jogadores"""
        try:
            conn = CoinsService.create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT nome, moedas FROM coins ORDER BY moedas DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print(f"Erro ao obter top players: {e}")
            return []
    
    @staticmethod
    def player_exists(nome: str) -> bool:
        """Verificar se jogador existe no sistema de moedas"""
        try:
            conn = CoinsService.create_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM coins WHERE nome = ?", (nome,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            print(f"Erro ao verificar existência de {nome}: {e}")
            return False

# Inicializar tabela ao importar
CoinsService.create_table()
