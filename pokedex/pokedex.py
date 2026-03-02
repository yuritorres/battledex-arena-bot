#!/usr/bin/env python3
"""
Pokedex CLI

Usage:
  pokedex [name_or_id]

Features:
  - Search by Pokémon name or ID
  - Display stats and basic info
  - Show sprite image URL and optionally open it in your browser
"""

import argparse
import requests
import sys
import webbrowser
import json
import os

API_URL = "https://pokeapi.co/api/v2/pokemon/{}"
STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
os.makedirs(STORAGE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(STORAGE_DIR, 'pokedex_cache.json')

def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}
        except Exception as e:
            print(f"[POKEDEX] Erro ao ler cache: {e}")
            return {}
    return {}

def _save_cache(cache):
    if not os.path.exists(STORAGE_DIR):
        print(f"[POKEDEX] Criando pasta de cache para salvar: {STORAGE_DIR}")
        os.makedirs(STORAGE_DIR, exist_ok=True)
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            print(f"[POKEDEX] Salvando cache em {CACHE_FILE}")
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[POKEDEX] Erro ao salvar cache: {e}")

def get_pokemon(identificador: str) -> dict:
    """
    Busca dados do Pokémon na PokeAPI pelo nome ou ID.
    Usa cache local em pokedex_cache.json para evitar requisições repetidas.
    Retorna um dicionário com os dados ou None se não encontrado.
    """
    identificador = identificador.lower()
    print(f"[POKEDEX] Buscando Pokémon: {identificador}")
    cache = _load_cache()
    if identificador in cache:
        print(f"[POKEDEX] Pokémon '{identificador}' encontrado no cache.")
        return cache[identificador]
    url = API_URL.format(identificador)
    print(f"[POKEDEX] Fazendo requisição para {url}")
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"[POKEDEX] Pokémon '{identificador}' não encontrado na API. Status: {resp.status_code}")
        return None
    data = resp.json()
    cache[identificador] = data
    _save_cache(cache)
    print(f"[POKEDEX] Pokémon '{identificador}' salvo no cache.")
    return data

def format_pokemon_info(data: dict) -> tuple[str, str|None]:
    """
    Formata as informações do Pokémon para mensagem no Telegram (em português).
    Retorna (mensagem_markdown, sprite_url).
    """
    nome = data.get('name', 'N/A').title()
    pid = data.get('id', 'N/A')
    tipos = ', '.join(t['type']['name'] for t in data.get('types', []))
    habilidades = ', '.join(a['ability']['name'] for a in data.get('abilities', []))
    stats = "\n".join(f"  {stat['stat']['name']}: {stat['base_stat']}" for stat in data.get('stats', []))
    experiencia_base = data.get('base_experience', 'N/A')
    altura = data.get('height', 'N/A')
    peso = data.get('weight', 'N/A')
    # Imagem oficial do Pokémon (official-artwork)
    try:
        pid_int = int(pid)
        sprite_url = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pid_int}.png"
    except Exception:
        sprite_url = None
    msg = (
        f"*Nome:* {nome}\n"
        f"*ID:* {pid}\n"
        f"*Tipos:* {tipos}\n"
        f"*Habilidades:* {habilidades}\n"
        f"*Status:*\n{stats}\n"
        f"*Experiência Base:* {experiencia_base}\n"
        f"*Altura:* {altura} dm\n"
        f"*Peso:* {peso} hg"
    )
    return msg, sprite_url
