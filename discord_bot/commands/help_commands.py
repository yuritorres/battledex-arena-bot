"""
Comandos de ajuda para Discord
"""

import discord
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

from discord.ext import commands

class HelpCommands(commands.Cog):
    """Commands de ajuda geral"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="ajuda", description="Ver ajuda geral do BattleDex Arena Bot")
    @app_commands.describe(categoria="Categoria específica de ajuda")
    async def ajuda(self, interaction: discord.Interaction, categoria: str = None):
        """Mostrar ajuda geral ou por categoria"""
        
        username = interaction.user.name
        
        logger.info(f"Comando /ajuda usado por {username}: {categoria or 'geral'}")
        
        # Categorias disponíveis
        categories = {
            "geral": self.help_geral,
            "ranking": self.help_ranking,
            "moedas": self.help_moedas,
            "loja": self.help_loja,
            "quiz": self.help_quiz,
            "ia": self.help_ia,
            "admin": self.help_admin
        }
        
        # Se categoria especificada, mostrar ajuda específica
        if categoria and categoria.lower() in categories:
            embed = categories[categoria.lower()](username)
        else:
            # Mostrar menu de categorias
            embed = discord.Embed(
                title="🤖 BattleDex Arena Bot - Ajuda",
                description=f"Olá **{username}**! Escolha uma categoria para ver os comandos:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 Categorias Disponíveis",
                value="• 🏆 `/ajuda ranking` - Sistema de ranking\n"
                      "• 💰 `/ajuda moedas` - Sistema de moedas\n"
                      "• 🛍️ `/ajuda loja` - Sistema de loja\n"
                      "• 🎯 `/ajuda quiz` - Sistema de quiz\n"
                      "• 🤖 `/ajuda ia` - Comandos de IA\n"
                      "• ⚙️ `/ajuda admin` - Comandos de admin\n"
                      "• 📖 `/ajuda geral` - Visão geral",
                inline=False
            )
            
            embed.add_field(
                name="🎮 Comandos Rápidos",
                value="• `/showranking` - Ver ranking ELO\n"
                      "• `/saldo` - Ver suas moedas\n"
                      "• `/quiz` - Iniciar quiz\n"
                      "• `/perguntar` - Perguntar à IA",
                inline=False
            )
        
        embed.set_footer(text="BattleDex Arena Bot v1.0 | Desenvolvido com ❤️")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def help_geral(self, username):
        """Ajuda geral"""
        embed = discord.Embed(
            title="📖 Ajuda Geral - BattleDex Arena Bot",
            description=f"Bem-vindo **{username}**! Sou um bot para gerenciar torneios de BattleDex.",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🚀 Como Começar",
            value="1. Use `/showranking` para ver o ranking atual\n"
                  "2. Use `/quiz` para testar seu conhecimento\n"
                  "3. Use `/saldo` para ver suas moedas\n"
                  "4. Participe de torneios para ganhar recompensas!",
            inline=False
        )
        
        embed.add_field(
            name="🎮 Principais Comandos",
            value="• `/showranking` - Ranking ELO\n"
                  "• `/quiz` - Quiz de BattleDex\n"
                  "• `/saldo` - Suas moedas\n"
                  "• `/perguntar` - Perguntar à IA\n"
                  "• `/ajuda` - Este menu de ajuda",
            inline=False
        )
        
        return embed
    
    def help_ranking(self, username):
        """Ajuda do sistema de ranking"""
        embed = discord.Embed(
            title="🏆 Ajuda - Sistema de Ranking",
            description="Gerencie o ranking ELO dos jogadores",
            color=discord.Color.orange()
        )
        
        commands_info = [
            ("📊 /showranking", "Mostrar ranking atual (todos)"),
            ("➕ /addplayer", "Adicionar jogador (admin)"),
            ("➖ /delplayer", "Remover jogador (admin)"),
            ("🔄 /resetelo", "Resetar ELO individual (admin)"),
            ("🔄 /reseteloall", "Resetar todos os ELOs (admin)"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        return embed
    
    def help_moedas(self, username):
        """Ajuda do sistema de moedas"""
        embed = discord.Embed(
            title="💰 Ajuda - Sistema de Moedas",
            description="Gerencie e use moedas virtuais",
            color=discord.Color.gold()
        )
        
        commands_info = [
            ("💸 /saldo", "Ver seu saldo de moedas"),
            ("💸 /enviarmoedas", "Enviar moedas para outros"),
            ("🏆 /rankingmoedas", "Ver ranking dos mais ricos"),
            ("💡 /ajudamoedas", "Ajuda detalhada de moedas"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        return embed
    
    def help_loja(self, username):
        """Ajuda do sistema de loja"""
        embed = discord.Embed(
            title="🛍️ Ajuda - Sistema de Loja",
            description="Compre itens com suas moedas",
            color=discord.Color.purple()
        )
        
        commands_info = [
            ("🛍️ /loja", "Ver itens disponíveis"),
            ("💳 /comprar", "Comprar um item"),
            ("🎒 /inventario", "Ver seu inventário"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        return embed
    
    def help_quiz(self, username):
        """Ajuda do sistema de quiz"""
        embed = discord.Embed(
            title="🎯 Ajuda - Sistema de Quiz",
            description="Teste seu conhecimento e ganhe moedas",
            color=discord.Color.green()
        )
        
        commands_info = [
            ("🎯 /quiz", "Iniciar um novo quiz"),
            ("💬 /responder", "Responder pergunta do quiz"),
            ("🏆 /rankingquiz", "Ver ranking de quiz"),
            ("💡 /ajudaquiz", "Ajuda detalhada de quiz"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        return embed
    
    def help_ia(self, username):
        """Ajuda do sistema de IA"""
        embed = discord.Embed(
            title="🤖 Ajuda - Sistema de IA",
            description="Use IA para tirar dúvidas e analisar jogadores",
            color=discord.Color.blue()
        )
        
        commands_info = [
            ("❓ /perguntar", "Fazer perguntas sobre BattleDex"),
            ("📊 /analisarjogador", "Analisar estatísticas de jogador"),
            ("💡 /dica", "Obter dicas de BattleDex"),
            ("🤖 /ajudaia", "Ajuda detalhada de IA"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        return embed
    
    def help_admin(self, username):
        """Ajuda dos comandos de admin"""
        embed = discord.Embed(
            title="⚙️ Ajuda - Comandos de Admin",
            description="Comandos restritos para administradores",
            color=discord.Color.red()
        )
        
        commands_info = [
            ("➕ /addplayer", "Adicionar jogador ao ranking"),
            ("➖ /delplayer", "Remover jogador do ranking"),
            ("🔄 /resetelo", "Resetar ELO individual"),
            ("🔄 /reseteloall", "Resetar todos os ELOs"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.add_field(
            name="🔐 Requisitos",
            value="Você precisa ter a role de administrador configurada no bot para usar estes comandos.",
            inline=False
        )
        
        return embed

async def setup(bot: commands.Bot):
    """Setup dos comandos de ajuda"""
    await bot.add_cog(HelpCommands(bot))
