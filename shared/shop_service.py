"""
BattleDex Arena - Shop Service
Serviço compartilhado para gerenciamento de loja
"""

import os
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
SHOP_DB_PATH = os.path.join(STORAGE_DIR, "shop.db")

class ShopService:
    """Serviço para gerenciamento de loja"""
    
    @staticmethod
    def create_connection():
        """Criar conexão com banco de dados"""
        os.makedirs(os.path.dirname(SHOP_DB_PATH), exist_ok=True)
        conn = sqlite3.connect(SHOP_DB_PATH)
        return conn
    
    @staticmethod
    def create_tables():
        """Criar tabelas da loja"""
        conn = ShopService.create_connection()
        cursor = conn.cursor()
        
        # Tabela de itens
        cursor.execute('''CREATE TABLE IF NOT EXISTS shop_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            price INTEGER NOT NULL,
            stock INTEGER DEFAULT 999,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Tabela de inventário
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, item_name)
        )''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def add_item(name: str, description: str, price: int, stock: int = 999) -> bool:
        """Adicionar item à loja"""
        try:
            conn = ShopService.create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO shop_items (name, description, price, stock)
                VALUES (?, ?, ?, ?)
            ''', (name, description, price, stock))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao adicionar item {name}: {e}")
            return False
    
    @staticmethod
    def get_all_items() -> List[Dict]:
        """Obter todos os itens da loja"""
        try:
            conn = ShopService.create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT name, description, price, stock FROM shop_items ORDER BY name')
            rows = cursor.fetchall()
            conn.close()
            
            items = []
            for row in rows:
                items.append({
                    'name': row[0],
                    'description': row[1],
                    'price': row[2],
                    'stock': row[3]
                })
            return items
        except Exception as e:
            print(f"Erro ao obter itens: {e}")
            return []
    
    @staticmethod
    def get_item(name: str) -> Optional[Dict]:
        """Obter item específico"""
        try:
            conn = ShopService.create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT name, description, price, stock FROM shop_items WHERE name = ?', (name,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'name': row[0],
                    'description': row[1],
                    'price': row[2],
                    'stock': row[3]
                }
            return None
        except Exception as e:
            print(f"Erro ao obter item {name}: {e}")
            return None
    
    @staticmethod
    def buy_item(user_id: str, item_name: str) -> bool:
        """Comprar item"""
        try:
            conn = ShopService.create_connection()
            cursor = conn.cursor()
            
            # Obter item
            cursor.execute('SELECT price, stock FROM shop_items WHERE name = ?', (item_name,))
            item_row = cursor.fetchone()
            
            if not item_row:
                conn.close()
                return False
            
            price, stock = item_row
            
            if stock <= 0:
                conn.close()
                return False
            
            # Verificar se usuário tem moedas suficientes
            from shared.coins_service import CoinsService
            user_balance = CoinsService.get_balance(user_id)
            
            if user_balance < price:
                conn.close()
                return False
            
            # Realizar compra
            if CoinsService.remove_coins(user_id, price):
                # Atualizar estoque
                cursor.execute('UPDATE shop_items SET stock = stock - 1 WHERE name = ?', (item_name,))
                
                # Adicionar ao inventário
                cursor.execute('''
                    INSERT OR REPLACE INTO user_inventory (user_id, item_name, quantity)
                    VALUES (?, ?, COALESCE((SELECT quantity FROM user_inventory WHERE user_id = ? AND item_name = ?), 0) + 1)
                ''', (user_id, item_name, user_id, item_name))
                
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
        except Exception as e:
            print(f"Erro ao comprar item {item_name}: {e}")
            return False
    
    @staticmethod
    def get_user_inventory(user_id: str) -> Dict[str, int]:
        """Obter inventário do usuário"""
        try:
            conn = ShopService.create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT item_name, quantity FROM user_inventory WHERE user_id = ?', (user_id,))
            rows = cursor.fetchall()
            conn.close()
            
            inventory = {}
            for row in rows:
                inventory[row[0]] = row[1]
            
            return inventory
        except Exception as e:
            print(f"Erro ao obter inventário de {user_id}: {e}")
            return {}
    
    @staticmethod
    def initialize_default_items():
        """Inicializar itens padrão da loja"""
        default_items = [
            ("Poção de Cura", "Recupera 50 HP em batalha", 100, 50),
            ("Boost de ELO", "Aumenta ELO em 10 pontos", 500, 10),
            ("Título de Mestre", "Título exclusivo no perfil", 1000, 5),
            ("Emoji Personalizado", "Emoji exclusivo do servidor", 200, 20),
            ("Entrada VIP", "Acesso a torneios VIP", 300, 15),
        ]
        
        for name, desc, price, stock in default_items:
            ShopService.add_item(name, desc, price, stock)

# Inicializar tabelas ao importar
ShopService.create_tables()
ShopService.initialize_default_items()
