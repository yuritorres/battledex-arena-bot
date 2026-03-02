import os
import json
from datetime import datetime
from financeiro.coins_db import add_coins

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
PARTICIPATION_FILE = os.path.join(STORAGE_DIR, "participation_bonus.json")
os.makedirs(STORAGE_DIR, exist_ok=True)

# Função para registrar participação diária
async def registrar_participacao(update, context):
    user_id = str(update.effective_user.id)
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(PARTICIPATION_FILE, "r", encoding="utf-8") as f:
            participations = json.load(f)
    except Exception:
        participations = {}
    # Garante que o histórico seja uma lista para cada usuário
    if user_id not in participations or not isinstance(participations[user_id], list):
        # Se for string (modelo antigo), converte para lista
        if isinstance(participations.get(user_id), str):
            participations[user_id] = [participations[user_id]]
        else:
            participations[user_id] = []
    # Se o usuário já participou hoje, não faz nada
    if today in participations[user_id]:
        return
    participations[user_id].append(today)
    with open(PARTICIPATION_FILE, "w", encoding="utf-8") as f:
        json.dump(participations, f, ensure_ascii=False, indent=4)
    # Buscar nome do ranking do usuário
    usuarios_path = os.path.join(STORAGE_DIR, "usuarios.json")
    try:
        with open(usuarios_path, "r", encoding="utf-8") as f:
            usuarios_map = json.load(f)
    except Exception:
        usuarios_map = {}
    nome = usuarios_map.get(user_id)
    if nome:
        add_coins(nome, 1)
        await update.message.reply_text("🎉 Parabéns! Você recebeu 1 BattleCoin por participar hoje no grupo.")
    else:
        await update.message.reply_text("⚠️ Seu ID não está vinculado ao ranking. Peça para um admin vincular você para receber bônus de participação.")
