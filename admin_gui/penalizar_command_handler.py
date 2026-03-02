from telegram.ext import ContextTypes
from telegram import Update
from config import ADMINS
from financeiro.coins_db import remove_coins, get_coins

MAX_COINS = 9_000_000_000_000_000_000

async def penalizar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("⛔ Apenas administradores podem penalizar participantes.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /penalizar <Usuário> <quantidade>")
        return
    nome_usuario = context.args[0]
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
    saldo_atual = get_coins(nome_usuario)
    if saldo_atual < quantidade:
        await update.message.reply_text(f"Saldo insuficiente. {nome_usuario} tem apenas {saldo_atual} moedas.")
        return
    remove_coins(nome_usuario, quantidade)
    novo_saldo = get_coins(nome_usuario)
    await update.message.reply_text(f"❗ {quantidade} moedas removidas de {nome_usuario}. Novo saldo: {novo_saldo}")
