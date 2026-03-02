import re
from typing import Tuple
from telegram import Update
from telegram.ext import ContextTypes

from tournaments_db import (
    create_tournament,
    set_status,
    list_tournaments,
    record_result,
    ranking,
    add_player,
)


def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    admins = context.application.bot_data.get("ADMINS", set())
    return update.effective_user and update.effective_user.id in admins


def _parse_result_lines(lines: list) -> Tuple[bool, Tuple[str, str, int, int, str] | str]:
    if len(lines) < 3:
        return False, "⚠️ Formato inválido. Use:\n/cmd <id>\nJogador1 X x Y Jogador2\nlink"
    header = lines[1]
    link = lines[2].strip()
    if not link.startswith("https://replay.pokemonshowdown.com/"):
        return False, "❌ Link inválido. Use replay do Showdown."
    m = re.match(r"([^\d]+?) (\d+) x (\d+) ([^\d]+)", header)
    if not m:
        return False, "⚠️ Formato inválido. Use 'Jogador1 X x Y Jogador2' na segunda linha."
    j1, s1, s2, j2 = m.groups()
    return True, (j1.strip(), j2.strip(), int(s1), int(s2), link)


async def cmd_criar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update, context):
        await update.message.reply_text("❌ Apenas administradores podem criar campeonatos.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /<cmd> <nome> [ano]")
        return
    nome = " ".join(context.args[:-1]) if len(context.args) > 1 else context.args[0]
    ano = None
    if len(context.args) > 1 and context.args[-1].isdigit():
        ano = int(context.args[-1])
        nome = " ".join(context.args[:-1])
    tid = create_tournament(nome, ano)
    await update.message.reply_text(f"✅ Campeonato criado (id={tid}). Status: draft.")


async def cmd_abrir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update, context):
        await update.message.reply_text("❌ Apenas administradores podem abrir campeonatos.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Uso: /<cmd> <id>")
        return
    tid = int(context.args[0])
    ok = set_status(tid, "ativo")
    await update.message.reply_text("✅ Campeonato aberto." if ok else "❌ Campeonato não encontrado.")


async def cmd_fechar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not _is_admin(update, context):
        await update.message.reply_text("❌ Apenas administradores podem fechar campeonatos.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Uso: /<cmd> <id>")
        return
    tid = int(context.args[0])
    ok = set_status(tid, "encerrado")
    await update.message.reply_text("✅ Campeonato encerrado." if ok else "❌ Campeonato não encontrado.")


async def cmd_listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = list_tournaments(limit=15)
    if not rows:
        await update.message.reply_text("Nenhum campeonato cadastrado.")
        return
    msg = "🏆 Campeonatos:\n"
    for tid, nome, ano, status, criado in rows:
        msg += f"- ID {tid} | {nome} ({ano or '-'}), status: {status}\n"
    await update.message.reply_text(msg)


async def cmd_resultado(update: Update, context: ContextTypes.DEFAULT_TYPE):
    linhas = update.message.text.splitlines()
    if not linhas or not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Uso: /<cmd> <id>\nJogador1 X x Y Jogador2\nlink")
        return
    tid = int(context.args[0])
    ok, parsed = _parse_result_lines(linhas)
    if not ok:
        await update.message.reply_text(parsed)
        return
    j1, j2, s1, s2, link = parsed
    success, msg = record_result(tid, j1, j2, s1, s2, link)
    await update.message.reply_text(msg)


async def cmd_addplayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2 or not context.args[0].isdigit():
        await update.message.reply_text("Uso: /<cmd> <id> <nome>")
        return
    tid = int(context.args[0])
    nome = " ".join(context.args[1:])
    add_player(tid, nome)
    await update.message.reply_text(f"✅ {nome} adicionado ao campeonato {tid}.")


async def cmd_ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Uso: /<cmd> <id>")
        return
    tid = int(context.args[0])
    rows = ranking(tid)
    if not rows:
        await update.message.reply_text("Nenhum jogador neste campeonato.")
        return
    msg = f"🏆 Ranking Campeonato {tid}:\n\n"
    for i, (nome, elo, vit, der, pts) in enumerate(rows, 1):
        medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"{i}."))
        msg += f"{medal} {nome} — Elo {elo} | 🟢 {vit} / 🔴 {der} | Pts {pts}\n"
    await update.message.reply_text(msg)
