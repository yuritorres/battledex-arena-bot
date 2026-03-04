import logging
import asyncio
import os
import re
import json
from dotenv import load_dotenv

from services.replay_analyzer import analyze_replay, format_player_stats
from utils.logger import setup_logger
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pokedex.pokedex_command_handler import pokedex_command
from services.ia_bot import ask_gemini
from quiz.quiz_service import register_quiz_handlers

logger = setup_logger()

# IDs de administradores

BASE_DIR = os.path.dirname(__file__)
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
USERS_JSON_PATH = os.path.join(STORAGE_DIR, "usuarios.json")
QUESTIONS_DB_PATH = os.path.join(STORAGE_DIR, "scores.db")
RANKING_DB_PATH = os.path.join(STORAGE_DIR, "rankingbf.db")
REPLAY_STATS_PATH = os.path.join(STORAGE_DIR, "replay_stats.json")
QUIZ_GROUP_ID_ENV = os.getenv("CHAT_ID_BF_ADM_QUIZ") or os.getenv("QUIZ_GROUP_ID")
QUIZ_TOPIC_ID_ENV = os.getenv("QUIZ_TOPIC_ID")
QUIZ_GROUP_ID = int(QUIZ_GROUP_ID_ENV) if QUIZ_GROUP_ID_ENV and QUIZ_GROUP_ID_ENV.lstrip('-').isdigit() else None
QUIZ_TOPIC_ID = int(QUIZ_TOPIC_ID_ENV) if QUIZ_TOPIC_ID_ENV and QUIZ_TOPIC_ID_ENV.lstrip('-').isdigit() else None
LOJA_GROUP_ID_ENV = os.getenv("LOJA_GROUP_ID")
LOJA_TOPIC_ID_ENV = os.getenv("LOJA_TOPIC_ID")
LOJA_GROUP_ID = int(LOJA_GROUP_ID_ENV) if LOJA_GROUP_ID_ENV and LOJA_GROUP_ID_ENV.lstrip('-').isdigit() else None
LOJA_TOPIC_ID = int(LOJA_TOPIC_ID_ENV) if LOJA_TOPIC_ID_ENV and LOJA_TOPIC_ID_ENV.lstrip('-').isdigit() else None

# Grupo para anúncios
BROADCAST_CHAT_ID_ENV = os.getenv("BROADCAST_CHAT_ID")
BROADCAST_CHAT_ID = int(BROADCAST_CHAT_ID_ENV) if BROADCAST_CHAT_ID_ENV and BROADCAST_CHAT_ID_ENV.lstrip('-').isdigit() else None
BROADCAST_TOPIC_ID_ENV = os.getenv("BROADCAST_TOPIC_ID")
BROADCAST_TOPIC_ID = int(BROADCAST_TOPIC_ID_ENV) if BROADCAST_TOPIC_ID_ENV and BROADCAST_TOPIC_ID_ENV.lstrip('-').isdigit() else None

# Comandos de campeonato configuráveis via .env
CAMP_CMD_CRIAR = os.getenv("CAMP_CMD_CRIAR", "/camp_criar")
CAMP_CMD_ABRIR = os.getenv("CAMP_CMD_ABRIR", "/camp_abrir")
CAMP_CMD_FECHAR = os.getenv("CAMP_CMD_FECHAR", "/camp_fechar")
CAMP_CMD_RESULTADO = os.getenv("CAMP_CMD_RESULTADO", "/camp_resultado")
CAMP_CMD_RANKING = os.getenv("CAMP_CMD_RANKING", "/camp_ranking")
CAMP_CMD_LISTA = os.getenv("CAMP_CMD_LISTA", "/camp_lista")
CAMP_CMD_ADDPLAYER = os.getenv("CAMP_CMD_ADDPLAYER", "/camp_addplayer")

os.makedirs(STORAGE_DIR, exist_ok=True)

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))
adm_env = os.getenv("ADMINS", "")

def _parse_admin_ids(raw):
    ids = []
    for entry in raw.split(","):
        cleaned = entry.strip()
        if not cleaned:
            continue
        if not cleaned.lstrip("-").isdigit():
            logger.warning("Ignorando entrada ADMINS inválida: %s", cleaned)
            continue
        try:
            ids.append(int(cleaned))
        except ValueError:
            logger.warning("Falha ao converter ADMINS: %s", cleaned)
    return ids

# Permite valor único ou lista separada por vírgula; ignora entradas vazias ou inválidas
ADMINS = _parse_admin_ids(adm_env)

from handlers.handlers_ranking import addplayer, dellplayer, showranking, resetelo, reseteloall
from repositories.ranking_db import calcular_pontos, add_player, update_elo, create_table
from repositories.tournaments_db import create_tables as create_tournaments_tables
from bonus.premios_command_handler import premio_command

from handlers.handlers_ranking_message import handle_message
from handlers.handlers_tournament import (
    cmd_criar as camp_cmd_criar,
    cmd_abrir as camp_cmd_abrir,
    cmd_fechar as camp_cmd_fechar,
    cmd_resultado as camp_cmd_resultado,
    cmd_ranking as camp_cmd_ranking,
    cmd_listar as camp_cmd_listar,
    cmd_addplayer as camp_cmd_addplayer,
)
from bonus.participation_bonus import registrar_participacao
from bonus.registrar_usuario import registrar_usuario

# Main
from financeiro.coins_db import add_coins, get_coins, remove_coins, coins_leaderboard
from telegram.ext import CommandHandler
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'loja'))
from loja.shop import listar_itens, IMAGES_DIR, buscar_item
from loja.comprar import comprar_item
from loja.inventario import listar_inventario

# Handler composto para bônus de participação + handle_message
async def bonus_and_handle_message(update, context):
    # Registrar todo usuário que mandar mensagem (grupo ou privado)
    registrar_usuario(update.effective_user)
    await registrar_participacao(update, context)
    # handle_message só processa comandos #ranking, mas o registro já foi feito acima
    await handle_message(update, context)


# Handler para mostrar informações de todos que interagiram
async def info_command(update, context):
    import json
    user = update.effective_user
    if user.id not in ADMINS:
        await update.message.reply_text("⛔ Você não tem permissão para usar este comando.")
        return
    usuarios_path = USERS_JSON_PATH
    try:
        with open(usuarios_path, "r", encoding="utf-8") as f:
            usuarios = json.load(f)
        if not usuarios:
            msg = "Nenhum usuário registrado ainda."
        else:
            msg = "<b>Usuários que já interagiram com o bot:</b>\n"
            for uid, info in usuarios.items():
                if isinstance(info, dict):
                    nome = info.get("nome", "?")
                    username = info.get("username", None)
                else:
                    nome = info
                    username = None
                linha = f"ID: <code>{uid}</code> | Nome: <b>{nome}</b>"
                if username:
                    linha += f" | @{username}"
                msg += linha + "\n"
        await context.bot.send_message(chat_id=user.id, text=msg, parse_mode="HTML")
        if update.effective_chat.type != "private":
            await update.message.reply_text("A lista de usuários que já interagiram foi enviada no seu privado!")
    except Exception as e:
        await update.message.reply_text(f"Não foi possível enviar mensagem privada ou ler o arquivo de usuários. Inicie uma conversa com o bot primeiro. Erro: {e}")


# Handler para mostrar todos os comandos
async def comandos_command(update, context):
    msg = (
        "<b>Comandos disponíveis:</b>\n"
        "/addplayer &lt;nome&gt; — Adiciona jogador ao ranking (admin)\n"
        "/dellplayer &lt;nome&gt; — Remove jogador do ranking (admin)\n"
        "/showranking — Mostra o ranking atual\n"
        "/resetelo &lt;nome&gt; — Reseta o elo de um jogador (admin)\n"
        "/reseteloall — Reseta o elo de todos os jogadores (admin)\n"
        "/transferir &lt;Usuário&gt; &lt;quantidade&gt; — Transfere battlecoins\n"
        "/inventario — Mostra seu inventário\n"
        "/comprar &lt;item&gt; — Compra um item da loja\n"
        "/loja — Lista itens disponíveis na loja\n"
        "/saldo — Mostra seu saldo de battlecoins\n"
        "/coinsranking — Ranking de battlecoins\n"
        "/replay &lt;link&gt; — Analisa replay do Showdown\n"
        "/replaystats &lt;nome&gt; [tier] — Estatísticas agregadas de replays\n"
        "/broadcast &lt;mensagem&gt; — Envia anúncio a todos que já interagiram (admin)\n"
        "/info — Lista todos os usuários registrados\n"
        "/ia &lt;mensagem&gt; — Responde usando Gemini IA (restrito ao Torres)\n"
        "/penalizar &lt;Usuário&gt; &lt;quantidade&gt; — Remove battlecoins de um participante (admin)\n"
        "/comandos — Mostra esta mensagem\n"
        "\n<b>Comandos de ranking também podem ser enviados como mensagem iniciando por #ranking</b>"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


# Broadcast admin-only
async def broadcast_command(update, context):
    user_id = update.effective_user.id
    if user_id not in ADMINS:
        await update.message.reply_text("⛔ Você não tem permissão para usar este comando.")
        return

    texto = " ".join(context.args).strip()
    if not texto:
        await update.message.reply_text("Uso: /broadcast <mensagem a ser enviada ao grupo de anúncios>")
        return

    if not BROADCAST_CHAT_ID:
        await update.message.reply_text("Defina BROADCAST_CHAT_ID no .env para onde o anúncio deve ser enviado.")
        return

    target_chat = BROADCAST_CHAT_ID
    thread_id = BROADCAST_TOPIC_ID or (update.message.message_thread_id if update.message else None)

    # Tenta com thread (se houver) e faz fallback sem thread quando o tópico não existir
    try:
        await context.bot.send_message(chat_id=target_chat, message_thread_id=thread_id, text=texto)
        await update.message.reply_text("✅ Anúncio publicado no grupo configurado.")
    except Exception as e:
        error_msg = str(e)
        # Se falhou por tópico inexistente, tenta sem thread
        if "Message thread not found" in error_msg or "message thread" in error_msg.lower():
            try:
                await context.bot.send_message(chat_id=target_chat, text=texto)
                await update.message.reply_text("✅ Anúncio publicado no grupo (sem tópico, fallback).")
                return
            except Exception as e2:
                await update.message.reply_text(f"Falha ao publicar o anúncio (fallback sem tópico): {e2}")
                return
        await update.message.reply_text(f"Falha ao publicar o anúncio: {e}")


# /replay command: fetch and analyze Showdown replay
async def replay_command(update, context):
    if not context.args:
        await update.message.reply_text("Uso: /replay <link do replay do Showdown>")
        return
    url = context.args[0]
    try:
        text, _ = analyze_replay(url, REPLAY_STATS_PATH)
        await update.message.reply_text(text)
    except Exception as exc:
        await update.message.reply_text(f"Falha ao analisar replay: {exc}")


# /replaystats command: show aggregated stats per player (optionally per tier)
async def replaystats_command(update, context):
    if not context.args:
        await update.message.reply_text("Uso: /replaystats <nome> [tier]")
        return
    nome = context.args[0]
    tier = context.args[1] if len(context.args) > 1 else None
    text = format_player_stats(REPLAY_STATS_PATH, nome, tier)
    await update.message.reply_text(text)

# Handler /start para onboarding
async def start_command(update, context):
    msg = (
        "👋 Bem-vindo ao BattleDex Arena!\n\n"
        "Use /comandos para ver a lista completa. Principais atalhos:\n"
        "• /addplayer &lt;nome&gt; — adiciona jogador (admin)\n"
        "• /showranking — mostra ranking ELO\n"
        "• /saldo — mostra suas battlecoins\n"
        "• /loja — lista itens\n"
        "• /inventario — mostra seu inventário\n"
        "• /ia &lt;mensagem&gt; — pergunta à IA (restrito)\n"
        "• /ping — teste rápido\n"
        "• /quiztest — envia quiz (admins, se quiz habilitado)\n\n"
        "Dica: mensagens iniciando com #ranking registram resultado (formato Jogador1 X x Y Jogador2)."
    )
    await update.message.reply_text(msg, parse_mode="HTML")

# Ping simples para healthcheck
async def ping_command(update, context):
    await update.message.reply_text("pong")

# Handler para penalizar participante (remover battlecoins)
from admin_gui.penalizar_command_handler import penalizar_command

# Handler para transferir battlecoins
async def transferir_command(update, context):
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /transferir <Usuário> <quantidade>")
        return
    destinatario_nome = context.args[0]
    remetente_id = str(update.effective_user.id)

    # Buscar nome do remetente no usuarios.json
    import json, os
    usuarios_path = USERS_JSON_PATH
    try:
        with open(usuarios_path, "r", encoding="utf-8") as f:
            usuarios_map = json.load(f)
    except Exception:
        usuarios_map = {}
    nome_remetente_ranking = usuarios_map.get(remetente_id)
    if not nome_remetente_ranking:
        await update.message.reply_text("Seu ID não está vinculado a nenhum nome no ranking. Peça para um admin corrigir ou faça uma partida para ser vinculado.")
        return

    # Buscar nomes do ranking
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM ranking")
    nomes_ranking = set(row[0] for row in cursor.fetchall())
    conn.close()

    if nome_remetente_ranking not in nomes_ranking:
        await update.message.reply_text("Seu nome não está registrado no ranking. Não é possível transferir battlecoins.")
        return
    if destinatario_nome not in nomes_ranking:
        await update.message.reply_text(f"Usuário '{destinatario_nome}' não está registrado para receber battlecoins.")
        return
    if destinatario_nome == nome_remetente_ranking:
        await update.message.reply_text("Você não pode transferir battlecoins para si mesmo.")
        return
    try:
        quantidade = int(context.args[1])
    except ValueError:
        await update.message.reply_text("A quantidade deve ser um número inteiro.")
        return
    # Não permitir transferência para si mesmo
    if nome_remetente_ranking == destinatario_nome:
        await update.message.reply_text("Você não pode transferir battlecoins para si mesmo!")
        return
    saldo_remetente = get_coins(nome_remetente_ranking)
    MAX_COINS = 9_000_000_000_000_000_000
    if quantidade <= 0:
        await update.message.reply_text("A quantidade deve ser maior que zero.")
        return
    if quantidade > MAX_COINS:
        await update.message.reply_text(f"A quantidade máxima permitida é {MAX_COINS} battlecoins.")
        return
    if saldo_remetente < quantidade:
        await update.message.reply_text(f"Saldo insuficiente. Você tem apenas {saldo_remetente} battlecoins.")
        return
    remove_coins(nome_remetente_ranking, quantidade)
    add_coins(destinatario_nome, quantidade)
    await update.message.reply_text(f"💸 {nome_remetente_ranking} transferiu {quantidade} battlecoins para {destinatario_nome}!")

# Handler para comando de IA
async def ia_command(update, context):
    # Limitar o comando apenas ao usuário Torres (ID 7562086063)
    if update.effective_user.id != 7562086063:
        await update.message.reply_text("⛔ Você não tem permissão para usar este comando.")
        return
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Envie o comando assim: /ia <sua pergunta>")
        return
    await update.message.reply_text("Pensando com Gemini IA...")
    resposta = ask_gemini(prompt)
    await update.message.reply_text(resposta)

# Handler para consultar saldo de battlecoins
async def saldo_command(update, context):
    import json, os
    usuarios_path = USERS_JSON_PATH
    nome = None
    if context.args:
        nome = context.args[0]
    else:
        # Busca nome do ranking pelo ID do usuário
        try:
            with open(usuarios_path, "r", encoding="utf-8") as f:
                usuarios_map = json.load(f)
        except Exception:
            usuarios_map = {}
        nome = usuarios_map.get(str(update.effective_user.id))
        if not nome:
            await update.message.reply_text("Seu ID não está vinculado a nenhum nome no ranking. Peça para um admin corrigir ou use /addplayer.")
            return
    saldo = get_coins(nome)
    if saldo is None or saldo == 0:
        # Verifica se o nome realmente existe no ranking (tabela ranking)
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM ranking WHERE nome = ?", (nome,))
        existe = cursor.fetchone()[0]
        conn.close()
        if not existe:
            await update.message.reply_text(f"Usuário '{nome}' não existe no ranking.")
            return
    await update.message.reply_text(f"💰 {nome} tem {saldo} battlecoins.")

# Handler para comando /inventario
async def inventario_command(update, context):
    import json, os
    usuarios_path = USERS_JSON_PATH
    try:
        with open(usuarios_path, "r", encoding="utf-8") as f:
            usuarios_map = json.load(f)
    except Exception:
        usuarios_map = {}
    nome_usuario = usuarios_map.get(str(update.effective_user.id))
    if not nome_usuario:
        await update.message.reply_text("Seu ID não está vinculado a nenhum nome no ranking. Peça para um admin corrigir ou use /addplayer.")
        return
    itens = listar_inventario(nome_usuario)
    if not itens:
        await update.message.reply_text("Seu inventário está vazio.")
        return
    msg = "\U0001F4E6 *Seu inventário:*\n"
    for id_item, quantidade in itens:
        item = buscar_item(id_item)
        nome = item[2] if item else id_item
        msg += f"- {nome} (x{quantidade})\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

# Handler para comando /comprar
async def comprar_command(update, context):
    import json, os
    usuarios_path = USERS_JSON_PATH
    # Verifica se o usuário está vinculado a um nome
    try:
        with open(usuarios_path, "r", encoding="utf-8") as f:
            usuarios_map = json.load(f)
    except Exception:
        usuarios_map = {}
    nome_usuario = usuarios_map.get(str(update.effective_user.id))
    if not nome_usuario:
        await update.message.reply_text("Seu ID não está vinculado a nenhum nome no ranking. Peça para um admin corrigir ou use /addplayer.")
        return
    if not context.args:
        await update.message.reply_text("Uso: /comprar <id_item>")
        return
    item_id = context.args[0]
    ok, msg = comprar_item(nome_usuario, item_id)
    await update.message.reply_text(msg, parse_mode="Markdown")

# Handler para comando /loja
async def loja_command(update, context):
    chat_id = update.effective_chat.id if update.effective_chat else None
    thread_id = update.message.message_thread_id if update.message else None

    # Restringe o comando ao grupo/tópico configurado (se fornecido)
    if LOJA_GROUP_ID and chat_id and chat_id != LOJA_GROUP_ID:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Este comando só pode ser usado no grupo/tópico da loja configurado.",
        )
        return
    if LOJA_TOPIC_ID:
        if thread_id != LOJA_TOPIC_ID:
            await context.bot.send_message(
                chat_id=chat_id,
                message_thread_id=thread_id,
                text="Este comando só pode ser usado no tópico da loja configurado.",
            )
            return

    itens = listar_itens()
    if not itens:
        await context.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text="A loja está vazia no momento.",
        )
        return
    for item in itens:
        id_, id_item, nome, preco, imagem = item
        msg = f"🛒 *{nome}*\n💸 Preço: {preco} battlecoins\nID: `{id_item}`"
        if imagem:
            img_path = os.path.join(IMAGES_DIR, imagem)
            if os.path.exists(img_path):
                with open(img_path, "rb") as img_file:
                    await context.bot.send_photo(
                        chat_id=chat_id,
                        message_thread_id=thread_id,
                        photo=img_file,
                        caption=msg,
                        parse_mode="Markdown",
                    )
                continue
        await context.bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text=msg,
            parse_mode="Markdown",
        )

# Handler para ranking de battlecoins
async def coinsranking_command(update, context):
    ranking = coins_leaderboard()
    if not ranking:
        await update.message.reply_text("Ninguém tem battlecoins ainda.")
        return
    msg = "🏆 Ranking de Moedas:\n\n"
    for i, (nome, battlecoins) in enumerate(ranking, 1):
        medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f"{i}."))
        msg += f"{medal} {nome} — {battlecoins} battlecoins\n"
    await update.message.reply_text(msg)

# Handler para comando /pokedex foi movido para pokedex_command_handler.py
# Para usar, importe pokedex_command de pokedex_command_handler.py

def main():
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    create_table()
    create_tournaments_tables()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Guarda admins para outros módulos (quiz)
    app.bot_data["ADMINS"] = set(ADMINS)

    app.add_handler(CommandHandler("addplayer", addplayer))
    app.add_handler(CommandHandler("dellplayer", dellplayer))
    app.add_handler(CommandHandler("showranking", showranking))
    app.add_handler(CommandHandler("resetelo", resetelo))
    app.add_handler(CommandHandler("reseteloall", reseteloall))

    # Comandos de campeonatos (nomes configuráveis via .env)
    app.add_handler(CommandHandler(CAMP_CMD_CRIAR.lstrip('/'), camp_cmd_criar))
    app.add_handler(CommandHandler(CAMP_CMD_ABRIR.lstrip('/'), camp_cmd_abrir))
    app.add_handler(CommandHandler(CAMP_CMD_FECHAR.lstrip('/'), camp_cmd_fechar))
    app.add_handler(CommandHandler(CAMP_CMD_RESULTADO.lstrip('/'), camp_cmd_resultado))
    app.add_handler(CommandHandler(CAMP_CMD_RANKING.lstrip('/'), camp_cmd_ranking))
    app.add_handler(CommandHandler(CAMP_CMD_LISTA.lstrip('/'), camp_cmd_listar))
    app.add_handler(CommandHandler(CAMP_CMD_ADDPLAYER.lstrip('/'), camp_cmd_addplayer))
    app.add_handler(CommandHandler("ia", ia_command))
    app.add_handler(CommandHandler("saldo", saldo_command))
    app.add_handler(CommandHandler("coinsranking", coinsranking_command))
    app.add_handler(CommandHandler("comandos", comandos_command))
    app.add_handler(CommandHandler("replay", replay_command))
    app.add_handler(CommandHandler("replaystats", replaystats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("transferir", transferir_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("loja", loja_command))
    app.add_handler(CommandHandler("comprar", comprar_command))
    app.add_handler(CommandHandler("inventario", inventario_command))
    app.add_handler(CommandHandler("premio", premio_command))  # Handler de prêmio para admins
    app.add_handler(CommandHandler("penalizar", penalizar_command))  # Handler de penalidade para admins
    app.add_handler(CommandHandler("pokedex", pokedex_command))
    # Quiz integrado (usa OPENAI_API_KEY e CHAT_ID_BF_ADM_QUIZ ou QUIZ_GROUP_ID)
    register_quiz_handlers(app, STORAGE_DIR, QUIZ_GROUP_ID, QUIZ_TOPIC_ID)
    # Handler pokedex foi movido para pokedex_command_handler.py
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, bonus_and_handle_message))

    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("\nBot finalizado com sucesso. Até logo!")
        try:
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                loop.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()

