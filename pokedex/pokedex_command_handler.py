from telegram.ext import CommandHandler, ContextTypes
from telegram import Update
from pokedex.pokedex import get_pokemon, format_pokemon_info

# Handler para comando /pokedex
async def pokedex_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import sys
    print("[TEL] Handler /pokedex foi chamado!")
    print("[TEL] sys.path:", sys.path)
    print("[TEL] get_pokemon module:", get_pokemon.__module__)
    if not context.args:
        await update.message.reply_text("Uso: /pokedex <nome_ou_id>")
        return
    identifier = context.args[0]
    print(f"[TEL] Argumento recebido: {identifier}")
    try:
        print("[TEL] Chamando get_pokemon...")
        data = get_pokemon(identifier)
        if not data:
            await update.message.reply_text(f"Pokémon '{identifier}' não encontrado.")
            return
        msg, sprite_url = format_pokemon_info(data)
        await update.message.reply_text(msg, parse_mode="Markdown")
        if sprite_url:
            name = data.get('name', identifier)
            await update.message.reply_photo(sprite_url, caption=f"Sprite de {name.title()}")
    except Exception as e:
        print(f"[TEL] Erro no handler pokedex_command: {e}")
        await update.message.reply_text(f"Erro ao buscar informações: {e}")
