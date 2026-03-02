import os
import sqlite3
import json

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, 'storage')

DB_PATHS = {
    'ranking': os.path.join(STORAGE_DIR, 'rankingbf.db'),
    'coins': os.path.join(STORAGE_DIR, 'coins.db'),
    'inventario': os.path.join(STORAGE_DIR, 'inventario.db'),
    'shop': os.path.join(STORAGE_DIR, 'shop.db'),
}

BONUS_JSON_PATH = os.path.join(STORAGE_DIR, 'participation_bonus.json')

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