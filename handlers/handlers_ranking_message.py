from repositories.ranking_db import calcular_pontos, add_player, update_elo
from financeiro.coins_db import add_coins
import os
import json
from telegram import Update
from telegram.ext import ContextTypes

BATTLE_COINS_REWARD = int(os.getenv("BATTLE_COINS_REWARD", "10"))

def get_usuarios_path():
    # Caminho para storage/usuarios.json na raiz do projeto
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "usuarios.json"))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Registrar todo usuário que interagir
    registrar_usuario = context.bot_data.get('registrar_usuario')
    if registrar_usuario:
        registrar_usuario(update.effective_user)
    texto = update.message.text
    if not texto.startswith("#ranking"):
        return

    partes = texto.splitlines()
    if len(partes) < 3:
        await update.message.reply_text("⚠️ Formato inválido.\nUse:\n#ranking\nJogador1 X x Y Jogador2\nlink")
        return

    resultado = partes[1]
    link = partes[2].strip()

    if not link.startswith("https://replay.pokemonshowdown.com/"):
        await update.message.reply_text("❌ Batalha ignorada: link do replay inválido ou ausente.")
        return

    from repositories.ranking_db import create_connection
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM replays WHERE url = ?", (link,))
    if cursor.fetchone():
        await update.message.reply_text("⚠️ Esta batalha já foi registrada anteriormente.")
        return

    import re
    match = re.match(r"([^\d]+?) (\d+) x (\d+) ([^\d]+)", resultado)
    if not match:
        await update.message.reply_text("⚠️ Formato inválido.\nUse:\n#ranking\nJogador1 X x Y Jogador2\nlink")
        return

    jogador1, x, y, jogador2 = match.groups()
    x, y = int(x), int(y)

    vencedor = jogador1 if x > y else jogador2
    perdedor = jogador2 if vencedor == jogador1 else jogador1
    pontos = calcular_pontos(max(x, y), min(x, y))

    add_player(jogador1)
    add_player(jogador2)

    elo_vencedor, elo_perdedor = update_elo(vencedor, perdedor, pontos, link)

    usuarios_path = get_usuarios_path()
    try:
        with open(usuarios_path, "r", encoding="utf-8") as f:
            usuarios_map = json.load(f)
    except Exception:
        usuarios_map = {}
    # Atualiza o vínculo ID->nome do vencedor
    if hasattr(update, 'effective_user') and update.effective_user and vencedor == update.effective_user.first_name:
        usuarios_map[str(update.effective_user.id)] = vencedor
        with open(usuarios_path, "w", encoding="utf-8") as f:
            json.dump(usuarios_map, f, ensure_ascii=False, indent=4)

    # Procurar o ID do vencedor pelo nome
    id_vencedor = None
    for uid, nome in usuarios_map.items():
        if nome == vencedor:
            id_vencedor = uid
            break
    if vencedor:
        add_coins(vencedor, BATTLE_COINS_REWARD)
        msg = (
            f"🔥 {vencedor} venceu a batalha!\n\n"
            f"📉 {perdedor}: {elo_perdedor + pontos} → {elo_perdedor} (-{pontos} por derrota)\n\n"
            f"📈 {vencedor}: {elo_vencedor - pontos} → {elo_vencedor} (+{pontos} por vitória)\n"
            f"💰 {vencedor} ganhou {BATTLE_COINS_REWARD} Battlecoins!"
        )
    else:
        msg = (
            f"🔥 {vencedor} venceu a batalha!\n\n"
            f"📉 {perdedor}: {elo_perdedor + pontos} → {elo_perdedor} (-{pontos} por derrota)\n\n"
            f"📈 {vencedor}: {elo_vencedor - pontos} → {elo_vencedor} (+{pontos} por vitória)\n"
            f"❗ Não foi possível atribuir moedas: {vencedor} não está registrado no usuarios.json."
        )
    await update.message.reply_text(msg)
