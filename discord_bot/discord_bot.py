"""
BattleDex Arena - Discord Implementation
Bot principal para Discord com funcionalidades compatíveis com o Telegram
"""

import os
import logging
import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    """Bot Discord para BattleDex Arena"""
    
    def __init__(self):
        # Configurar intents necessários
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.token = os.getenv('DISCORD_BOT_TOKEN')
        self.admin_role_id = os.getenv('DISCORD_ADMIN_ROLE_ID')
        
    async def setup_hook(self):
        """Configuração inicial do bot"""
        logger.info("Configurando Discord Bot...")
        
        # Carregar comandos
        await self.load_commands()
        
        # Sincronizar comandos com Discord
        await self.tree.sync()
        
        logger.info("Discord Bot configurado com sucesso!")
    
    async def load_commands(self):
        """Carregar todos os módulos de comandos"""
        try:
            # Carregar comandos de ranking
            from discord_bot.commands.ranking_commands import setup
            await setup(self)
            logger.info("Comandos de ranking carregados!")
            
        except Exception as e:
            logger.error(f"Erro ao carregar comandos: {e}")
    
    async def on_ready(self):
        """Evento quando bot está pronto"""
        logger.info(f'Discord Bot conectado como {self.user}')
        logger.info(f'Bot está em {len(self.guilds)} servidores')
        
        # Definir status do bot
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="batalhas Pokémon | /showranking"
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Tratamento de erros de comandos"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignorar comandos não encontrados
        
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para usar este comando!")
            return
        
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Argumento obrigatório faltando!")
            return
        
        # Log do erro
        logger.error(f"Erro no comando {ctx.command}: {error}")
        await ctx.send("❌ Ocorreu um erro ao executar este comando!")
    
    def is_admin(self, member: discord.Member) -> bool:
        """Verificar se membro é admin"""
        if not self.admin_role_id:
            return False
        
        admin_role = member.guild.get_role(int(self.admin_role_id))
        return admin_role in member.roles
    
    async def start_bot(self):
        """Iniciar o bot Discord"""
        if not self.token:
            logger.error("DISCORD_TOKEN não encontrado nas variáveis de ambiente!")
            return
        
        await self.start(self.token)

def create_discord_bot():
    """Criar instância do bot Discord"""
    return DiscordBot()
