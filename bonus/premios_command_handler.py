from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
from financeiro.coins_db import add_coins, get_coins
from config import ADMINS

async def premio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Apenas administradores podem usar
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("⛔ Apenas administradores podem enviar prêmios em moedas virtuais.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /premio <nome_do_usuario> <quantidade>")
        return
    nome_usuario = context.args[0]
    MAX_COINS = 9_000_000_000_000_000_000
    try:
        quantidade = int(context.args[1])
    except ValueError:
        await update.message.reply_text("A quantidade deve ser um número inteiro.")
        return
    if quantidade <= 0:
        await update.message.reply_text("A quantidade deve ser maior que zero.")
        return
    if quantidade > MAX_COINS:
        await update.message.reply_text(f"A quantidade máxima permitida é {MAX_COINS} moedas.")
        return
    add_coins(nome_usuario, quantidade)
    saldo = get_coins(nome_usuario)
    await update.message.reply_text(f"🏆 {quantidade} moedas virtuais enviadas para {nome_usuario}! Novo saldo: {saldo}")

# Para registrar no main:
# from bonus.premios_command_handler import premio_command
# app.add_handler(CommandHandler("premio", premio_command))
