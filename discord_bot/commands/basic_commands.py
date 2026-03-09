"""
Comandos básicos para Discord (funcionam com serviços existentes)
"""

import discord
from discord import app_commands
import logging
import random

logger = logging.getLogger(__name__)

from discord.ext import commands

class BasicCommands(commands.Cog):
    """Commands básicos que funcionam imediatamente"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="ping", description="Testar se o bot está respondendo")
    async def ping(self, interaction: discord.Interaction):
        """Comando de ping simples"""
        await interaction.response.send_message("🏓 Pong! Bot está funcionando! 🤖")
        logger.info(f"Comando /ping usado por {interaction.user.name}")
    
    @app_commands.command(name="info", description="Ver informações do BattleDex Arena Bot")
    async def info(self, interaction: discord.Interaction):
        """Mostrar informações do bot"""
        
        embed = discord.Embed(
            title="🤖 BattleDex Arena Bot",
            description="Bot completo para gerenciamento de torneios de BattleDex",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎮 Funcionalidades",
            value="• 🏆 Sistema de Ranking ELO\n"
                  "• 💰 Sistema de Moedas\n"
                  "• 🛍️ Loja Virtual\n"
                  "• 🎯 Quiz Interativo\n"
                  "• 🤖 Assistente de IA\n"
                  "• 📊 Análise de Estatísticas",
            inline=False
        )
        
        embed.add_field(
            name="📋 Comandos Principais",
            value="• `/showranking` - Ver ranking\n"
                  "• `/quiz` - Iniciar quiz\n"
                  "• `/ping` - Testar bot\n"
                  "• `/ajuda` - Ver ajuda",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Versão",
            value="v1.0.0 - Discord + Telegram Integration",
            inline=False
        )
        
        embed.set_footer(text="Desenvolvido com ❤️ para comunidade BattleDex")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dado", description="Rolar um dado")
    @app_commands.describe(lados="Número de lados do dado (padrão: 6)")
    async def dado(self, interaction: discord.Interaction, lados: int = 6):
        """Rolar um dado com número personalizado de lados"""
        
        if lados < 2 or lados > 100:
            await interaction.response.send_message(
                "❌ O dado deve ter entre 2 e 100 lados!",
                ephemeral=True
            )
            return
        
        resultado = random.randint(1, lados)
        
        embed = discord.Embed(
            title="🎲 Dado Rolado!",
            description=f"**{interaction.user.name}** rolou um D{lados}",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="🎯 Resultado",
            value=f"**{resultado}**",
            inline=False
        )
        
        embed.set_thumbnail(url="https://emoji.discord.stuff/🎲")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="sorteio", description="Sortear um número aleatório")
    @app_commands.describe(minimo="Valor mínimo", maximo="Valor máximo")
    async def sorteio(self, interaction: discord.Interaction, minimo: int = 1, maximo: int = 100):
        """Sortear número aleatório em um intervalo"""
        
        if minimo >= maximo:
            await interaction.response.send_message(
                "❌ O valor mínimo deve ser menor que o máximo!",
                ephemeral=True
            )
            return
        
        if maximo - minimo > 1000000:
            await interaction.response.send_message(
                "❌ O intervalo é muito grande! Use no máximo 1.000.000 de diferença.",
                ephemeral=True
            )
            return
        
        resultado = random.randint(minimo, maximo)
        
        embed = discord.Embed(
            title="🎰 Sorteio Realizado!",
            description=f"**{interaction.user.name}** sorteou entre {minimo} e {maximo}",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🎯 Número Sorteado",
            value=f"**{resultado}**",
            inline=False
        )
        
        embed.add_field(
            name="📊 Probabilidade",
            value=f"1 em {maximo - minimo + 1} chances",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="calcular", description="Calcular expressões matemáticas simples")
    @app_commands.describe(expressao="Expressão matemática (ex: 2+2*3)")
    async def calcular(self, interaction: discord.Interaction, expressao: str):
        """Calcular expressões matemáticas simples"""
        
        try:
            # Permitir apenas operações seguras
            allowed_chars = set('0123456789+-*/().() ')
            if not all(c in allowed_chars for c in expressao):
                await interaction.response.send_message(
                    "❌ Apenas números e operações básicas (+, -, *, /) são permitidas!",
                    ephemeral=True
                )
                return
            
            # Avaliar expressão de forma segura
            resultado = eval(expressao)
            
            embed = discord.Embed(
                title="🧮 Calculadora",
                description=f"**{interaction.user.name}** calculou:",
                color=discord.Color.orange()
            )
            
            embed.add_field(
                name="📝 Expressão",
                value=f"```{expressao}```",
                inline=False
            )
            
            embed.add_field(
                name="✅ Resultado",
                value=f"**{resultado}**",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao calcular: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(name="ajudabasica", description="Ver ajuda dos comandos básicos")
    async def ajudabasica(self, interaction: discord.Interaction):
        """Mostrar ajuda dos comandos básicos"""
        
        embed = discord.Embed(
            title="📖 Ajuda - Comandos Básicos",
            description="Comandos disponíveis imediatamente",
            color=discord.Color.blue()
        )
        
        commands_info = [
            ("🏓 /ping", "Testar se o bot está respondendo"),
            ("ℹ️ /info", "Ver informações do bot"),
            ("🎲 /dado", "Rolar um dado (padrão: 6 lados)"),
            ("🎰 /sorteio", "Sortear número aleatório"),
            ("🧮 /calcular", "Calcular expressões matemáticas"),
            ("📖 /ajudabasica", "Ver esta ajuda"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.add_field(
            name="💡 Dica",
            value="Use `/ajuda` para ver todos os comandos disponíveis!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup dos comandos básicos"""
    await bot.add_cog(BasicCommands(bot))
