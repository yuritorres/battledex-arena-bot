import logging
import asyncio
import os
import re
import sqlite3
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pokedex.pokedex_command_handler import pokedex_command
from ia_bot import ask_gemini

# Configuração do log com timezone de Brasília
class BrasiliaFormatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        return dt.replace(tzinfo=pytz.utc).astimezone(brasilia_tz)
        
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime('%Y-%m-%d %H:%M:%S')
        return s

formatter = BrasiliaFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)
# Ocultar logs de HTTP requests de httpx e urllib3
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# IDs de administradores
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(__file__)
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
USERS_JSON_PATH = os.path.join(STORAGE_DIR, "usuarios.json")
QUESTIONS_DB_PATH = os.path.join(STORAGE_DIR, "scores.db")
RANKING_DB_PATH = os.path.join(STORAGE_DIR, "rankingbf.db")

os.makedirs(STORAGE_DIR, exist_ok=True)

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))
ADMINS = [int(x.strip()) for x in os.getenv("ADMINS", "").split(",")]

# Caminho do banco de dados
DB_PATH = RANKING_DB_PATH

# Conectar ao banco de dados
def create_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

# Criar tabela se não existir
def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ranking (
        nome TEXT PRIMARY KEY,
        elo INTEGER DEFAULT 1000,
        vitorias INTEGER DEFAULT 0,
        derrotas INTEGER DEFAULT 0
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS replays (
        url TEXT PRIMARY KEY
    )''')
    conn.commit()
    conn.close()

# Handlers de comandos de ranking agora estão em handlers_ranking.py
from handlers_ranking import addplayer, dellplayer, showranking, resetelo, reseteloall
from ranking_db import calcular_pontos, add_player, update_elo
from bonus.premios_command_handler import premio_command

# Handler handle_message foi movido para handlers_ranking_message.py
from handlers_ranking_message import handle_message
from bonus.participation_bonus import registrar_participacao
from bonus.registrar_usuario import registrar_usuario

# Main
from dotenv import load_dotenv
#from ia_bot import ask_gemini
from financeiro.coins_db import add_coins, get_coins, remove_coins, coins_leaderboard
from telegram.ext import CommandHandler
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'loja'))
from loja.shop import listar_itens, IMAGES_DIR, buscar_item
from loja.comprar import comprar_item
from loja.inventario import listar_inventario
import sqlite3

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
    from dotenv import load_dotenv
    import os
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
    ADMINS = [int(x.strip()) for x in os.getenv("ADMINS", "").split(",") if x.strip().isdigit()]
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
        "/info — Lista todos os usuários registrados\n"
        "/ia &lt;mensagem&gt; — Responde usando Gemini IA (restrito ao Torres)\n"
        "/penalizar &lt;Usuário&gt; &lt;quantidade&gt; — Remove battlecoins de um participante (admin)\n"
        "/comandos — Mostra esta mensagem\n"
        "\n<b>Comandos de ranking também podem ser enviados como mensagem iniciando por #ranking</b>"
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
    itens = listar_itens()
    if not itens:
        await update.message.reply_text("A loja está vazia no momento.")
        return
    for item in itens:
        id_, id_item, nome, preco, imagem = item
        msg = f"🛒 *{nome}*\n💸 Preço: {preco} battlecoins\nID: `{id_item}`"
        if imagem:
            img_path = os.path.join(IMAGES_DIR, imagem)
            if os.path.exists(img_path):
                with open(img_path, "rb") as img_file:
                    await update.message.reply_photo(img_file, caption=msg, parse_mode="Markdown")
                continue
        await update.message.reply_text(msg, parse_mode="Markdown")

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
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("addplayer", addplayer))
    app.add_handler(CommandHandler("dellplayer", dellplayer))
    app.add_handler(CommandHandler("showranking", showranking))
    app.add_handler(CommandHandler("resetelo", resetelo))
    app.add_handler(CommandHandler("reseteloall", reseteloall))
    app.add_handler(CommandHandler("ia", ia_command))
    app.add_handler(CommandHandler("saldo", saldo_command))
    app.add_handler(CommandHandler("coinsranking", coinsranking_command))
    app.add_handler(CommandHandler("comandos", comandos_command))
    app.add_handler(CommandHandler("ping", ping_command))
    app.add_handler(CommandHandler("transferir", transferir_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("loja", loja_command))
    app.add_handler(CommandHandler("comprar", comprar_command))
    app.add_handler(CommandHandler("inventario", inventario_command))
    app.add_handler(CommandHandler("premio", premio_command))  # Handler de prêmio para admins
    app.add_handler(CommandHandler("penalizar", penalizar_command))  # Handler de penalidade para admins
    app.add_handler(CommandHandler("pokedex", pokedex_command))
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

import os
import re
import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configuração do log com timezone de Brasília
class BrasiliaFormatter(logging.Formatter):
    def converter(self, timestamp):
        dt = datetime.fromtimestamp(timestamp)
        brasilia_tz = pytz.timezone('America/Sao_Paulo')
        return dt.replace(tzinfo=pytz.utc).astimezone(brasilia_tz)
        
    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.strftime('%Y-%m-%d %H:%M:%S')
        return s

formatter = BrasiliaFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

from dotenv import load_dotenv

from config import ADMINS

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "rankingbf.db")

# Conectar ao banco de dados


def create_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn

# Criar tabela se não existir


def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS ranking (
        nome TEXT PRIMARY KEY,
        elo INTEGER DEFAULT 1000,
        vitorias INTEGER DEFAULT 0,
        derrotas INTEGER DEFAULT 0
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS replays (
        url TEXT PRIMARY KEY
    )''')
    conn.commit()
    conn.close()

# Adicionar jogador
def add_player(nome):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO ranking (nome) VALUES (?)", (nome,))
    conn.commit()
    conn.close()

# Remover jogador
def remove_player(nome):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ranking WHERE nome = ?", (nome,))
    conn.commit()
    conn.close()

# Mostrar ranking
def get_ranking():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT nome, elo, vitorias, derrotas FROM ranking ORDER BY elo DESC")
    rows = cursor.fetchall()
    conn.close()

    ranking_msg = "📊 Ranking BF 🔰\n\n"
    for i, row in enumerate(rows, 1):
        medal = "⭐️" if i == 1 else f"{i}."
        ranking_msg += f"{medal} {row[0]} - Elo: {row[1]} | 🟢 {row[2]} / 🔴 {row[3]}\n"
    return ranking_msg if rows else "Nenhum jogador no ranking."

# Atualizar ELO e salvar replay
def update_elo(vencedor, perdedor, pontos, link):
    print(f"[DEBUG][update_elo] Iniciando atualização: vencedor={vencedor}, perdedor={perdedor}, pontos={pontos}, link={link}")
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE ranking SET elo = elo + ?, vitorias = vitorias + 1 WHERE nome = ?", (pontos, vencedor))
        print(f"[DEBUG][update_elo] Atualizado vencedor: {vencedor} +{pontos} elo, +1 vitória")
        cursor.execute(
            "UPDATE ranking SET elo = elo - ?, derrotas = derrotas + 1 WHERE nome = ?", (pontos, perdedor))
        print(f"[DEBUG][update_elo] Atualizado perdedor: {perdedor} -{pontos} elo, +1 derrota")
        cursor.execute("INSERT OR IGNORE INTO replays (url) VALUES (?)", (link,))
        print(f"[DEBUG][update_elo] Replay registrado (ou ignorado se já existia): {link}")

        cursor.execute("SELECT elo FROM ranking WHERE nome = ?", (vencedor,))
        elo_vencedor = cursor.fetchone()[0]
        cursor.execute("SELECT elo FROM ranking WHERE nome = ?", (perdedor,))
        elo_perdedor = cursor.fetchone()[0]
        print(f"[DEBUG][update_elo] ELOs após atualização: vencedor={elo_vencedor}, perdedor={elo_perdedor}")

        conn.commit()
        print(f"[DEBUG][update_elo] Commit realizado com sucesso.")
        conn.close()
        print(f"[DEBUG][update_elo] Conexão fechada.")
        return elo_vencedor, elo_perdedor
    except Exception as e:
        print(f"[ERRO][update_elo] Falha ao atualizar ELO/replay: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

# Calcular pontos com base no placar


# Função calcular_pontos removida (usar import de ranking_db)

# Handlers
async def addplayer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /addplayer <nome>")
        return
    nome = context.args[0]
    add_player(nome)
    # Vincular ID ao nome do ranking
    import json, os
    usuarios_path = USERS_JSON_PATH
    try:
        with open(usuarios_path, "r", encoding="utf-8") as f:
            usuarios_map = json.load(f)
    except Exception:
        usuarios_map = {}
    usuarios_map[str(update.effective_user.id)] = nome
    with open(usuarios_path, "w", encoding="utf-8") as f:
        json.dump(usuarios_map, f, ensure_ascii=False, indent=4)
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
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE ranking SET elo = 1000, vitorias = 0, derrotas = 0")
    conn.commit()
    conn.close()
    await update.message.reply_text("🔄 Todos os jogadores tiveram seus Elos resetados para 1000!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[DEBUG] Handler chamado!")
    texto = update.message.text
    print("[DEBUG] Texto recebido:", texto)
    if not texto.startswith("#ranking"):
        print("[DEBUG] Ignorado: não começa com #ranking")
        return

    partes = texto.splitlines()
    print("[DEBUG] Partes:", partes)
    if len(partes) < 3:
        await update.message.reply_text("⚠️ Formato inválido.\nUse:\n#ranking\nJogador1 X x Y Jogador2\nlink")
        print("[DEBUG] Menos de 3 linhas")
        return

    resultado = partes[1]
    link = partes[2].strip()
    print(f"[DEBUG] Resultado: {resultado}")
    print(f"[DEBUG] Link: {link}")

    if not re.match(r"https://replay\.pokemonshowdown\.com/", link):
        await update.message.reply_text("❌ Batalha ignorada: link do replay inválido ou ausente.")
        print("[DEBUG] Link inválido")
        return

    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM replays WHERE url = ?", (link,))
    if cursor.fetchone():
        await update.message.reply_text("⚠️ Esta batalha já foi registrada anteriormente.")
        print("[DEBUG] Replay já registrado")
        return

    # Usando o regex do tel_base.py para nomes sem espaços
    match = re.match(r"(\w+) (\d+) x (\d+) (\w+)", resultado)
    print("[DEBUG] Match do regex:", match.groups() if match else "NÃO CASOU")
    if not match:
        await update.message.reply_text("⚠️ Formato inválido.\nUse:\n#ranking\nJogador1 X x Y Jogador2\nlink")
        print("[DEBUG] Regex não casou")
        return

    jogador1, x, y, jogador2 = match.groups()
    print(f"[DEBUG] jogador1: {jogador1}, x: {x}, y: {y}, jogador2: {jogador2}")
    x, y = int(x), int(y)

    vencedor = jogador1 if x > y else jogador2
    perdedor = jogador2 if vencedor == jogador1 else jogador1
    pontos = calcular_pontos(max(x, y), min(x, y))
    print(f"[DEBUG] vencedor: {vencedor}, perdedor: {perdedor}, pontos: {pontos}")

    add_player(jogador1)
    add_player(jogador2)

    elo_vencedor, elo_perdedor = update_elo(vencedor, perdedor, pontos, link)
    print(f"[DEBUG] elo_vencedor: {elo_vencedor}, elo_perdedor: {elo_perdedor}")

    msg = (
        f"🔥 {vencedor} venceu a batalha!\n\n"
        f"📉 {perdedor}: {elo_perdedor + pontos} → {elo_perdedor} (-{pontos} por derrota)\n\n"
        f"📈 {vencedor}: {elo_vencedor - pontos} → {elo_vencedor} (+{pontos} por vitória)"
    )
    await update.message.reply_text(msg)
    print("[DEBUG] Mensagem enviada para o usuário")

# Main


from dotenv import load_dotenv

def main():
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    create_table()
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("addplayer", addplayer))
    app.add_handler(CommandHandler("dellplayer", dellplayer))
    app.add_handler(CommandHandler("showranking", showranking))
    app.add_handler(CommandHandler("resetelo", resetelo))
    app.add_handler(CommandHandler("reseteloall", reseteloall))
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

    app.add_handler(CommandHandler("showranking", showranking))
    app.add_handler(CommandHandler("resetelo", resetelo))
    app.add_handler(CommandHandler("reseteloall", reseteloall))
    app.add_handler(CommandHandler("ia", ia_command))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, bonus_and_handle_message))

    try:
        app.run_polling()
    except KeyboardInterrupt:
        print("\nBot finalizado com sucesso. Até logo!")
        loop = asyncio.get_event_loop()
        if not loop.is_closed():
            loop.close()
    except Exception:
        pass


if __name__ == '__main__':
    main()
