import os
import sqlite3
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DB_PATHS = {
    'ranking': os.path.join(BASE_DIR, 'rankingbf.db'),
    'coins': os.path.join(BASE_DIR, 'financeiro', 'coins.db'),
    'inventario': os.path.join(BASE_DIR, 'loja', 'inventario.db'),
    'shop': os.path.join(BASE_DIR, 'loja', 'shop.db'),
}

BONUS_JSON_PATH = os.path.join(BASE_DIR, 'bonus', 'participation_bonus.json')

# Funções utilitárias para conexão

def get_connection(db_key):
    path = DB_PATHS.get(db_key)
    if not path:
        raise ValueError(f'DB não encontrado: {db_key}')
    return sqlite3.connect(path)

def read_participation_bonus():
    try:
        with open(BONUS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}