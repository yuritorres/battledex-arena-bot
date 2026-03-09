"""
Comandos de teste para Discord
"""

import discord
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

class TestCommands(discord.Cog):
    """Comandos de teste"""
    
    def __init__(self, bot: discord.Client):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Testar se o bot responde")
    async def ping(self, interaction: discord.Interaction):
        """Comando de ping simples"""
        await interaction.response.send_message("🏓 Pong! Bot está funcionando!")
        logger.info(f"Comando /ping usado por {interaction.user.name}")

async def setup(bot: discord.Client):
    """Setup dos comandos de teste"""
    await bot.add_cog(TestCommands(bot))
