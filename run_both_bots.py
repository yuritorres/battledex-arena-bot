"""
BattleDex Arena - Run Both Bots
Script para rodar Telegram e Discord bots simultaneamente
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

async def run_telegram_bot():
    """Rodar bot Telegram"""
    try:
        logger.info("Iniciando Telegram Bot...")
        
        # Importar e rodar main.py
        import main
        await main.main()
        
    except Exception as e:
        logger.error(f"Erro no Telegram Bot: {e}")

async def run_discord_bot():
    """Rodar bot Discord"""
    try:
        logger.info("Iniciando Discord Bot...")
        
        # Criar e iniciar bot Discord
        bot = create_discord_bot()
        await bot.start_bot()
        
        logger.info("Discord Bot iniciado com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro no Discord Bot: {e}")

async def main():
    """Função principal - rodar ambos os bots"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Verificar tokens
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    discord_token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not telegram_token:
        logger.error("TELEGRAM_TOKEN não encontrado!")
        return
    
    if not discord_token:
        logger.error("DISCORD_BOT_TOKEN não encontrado!")
        return
    
    logger.info("Iniciando BattleDex Arena - Telegram + Discord")
    
    try:
        # Rodar ambos os bots simultaneamente
        await asyncio.gather(
            run_telegram_bot(),
            run_discord_bot(),
            return_exceptions=True
        )
    except KeyboardInterrupt:
        logger.info("Bots encerrados pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bots encerrados pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
