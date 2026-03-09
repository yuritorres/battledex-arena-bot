"""
BattleDex Arena - Discord Bot Main
Script principal para iniciar o bot Discord
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from discord.discord_bot import create_discord_bot

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    """Função principal do bot Discord"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar token
    discord_token = os.getenv('DISCORD_BOT_TOKEN')
    if not discord_token:
        logger.error("DISCORD_BOT_TOKEN não encontrado no arquivo .env!")
        return
    
    # Criar e iniciar bot
    bot = create_discord_bot()
    
    try:
        logger.info("Iniciando Discord Bot...")
        await bot.start_bot()
    except Exception as e:
        logger.error(f"Erro ao iniciar bot Discord: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot Discord encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
