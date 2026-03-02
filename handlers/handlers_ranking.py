from telegram import Update
from telegram.ext import ContextTypes
from ranking_db import add_player, remove_player, get_ranking, update_elo, calcular_pontos
from config import ADMINS

async def addplayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return
    if len(context.args) >= 1:
        nome = " ".join(context.args)
    elif len(context.args) == 0:
        nome = update.effective_user.first_name
    else:
        await update.message.reply_text("Uso: /addplayer <nome>")
        return
    add_player(nome)
    await update.message.reply_text(f"✅ Jogador {nome} adicionado com Elo 1000!")

async def dellplayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /dellplayer <nome>")
        return
    nome = context.args[0]
    remove_player(nome)
    await update.message.reply_text(f"✅ Jogador {nome} foi removido do ranking!")

async def showranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_ranking())

async def resetelo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /resetelo <nome>")
        return
    nome = context.args[0]
    from ranking_db import create_connection
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE ranking SET elo = 1000, vitorias = 0, derrotas = 0 WHERE nome = ?", (nome,))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"🔄 Elo de {nome} foi resetado para 1000!")

async def reseteloall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return
    from ranking_db import create_connection
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE ranking SET elo = 1000, vitorias = 0, derrotas = 0")
    conn.commit()
    conn.close()
    await update.message.reply_text("🔄 Todos os jogadores tiveram seus Elos resetados para 1000!")
