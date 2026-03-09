"""
Comandos de moedas para Discord
"""

import discord
from discord import app_commands
import logging

from shared.coins_service import CoinsService

logger = logging.getLogger(__name__)

from discord.ext import commands

class CoinsCommands(commands.Cog):
    """Commands para sistema de moedas"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="saldo", description="Verificar seu saldo de moedas")
    async def saldo(self, interaction: discord.Interaction):
        """Verificar saldo de moedas do usuário"""
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        
        logger.info(f"Comando /saldo usado por {username}")
        
        try:
            # Obter saldo do serviço
            balance = CoinsService.get_balance(user_id)
            
            # Obter ranking de moedas
            ranking = CoinsService.get_top_balance(10)
            
            # Criar embed
            embed = discord.Embed(
                title="💰 Sistema de Moedas",
                description=f"Saldo de **{username}**",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="💸 Seu Saldo",
                value=f"🪙 {balance} moedas",
                inline=False
            )
            
            # Adicionar top 5 do ranking
            if ranking:
                embed.add_field(
                    name="🏆 Top 5 Ricões",
                    value="\n".join([f"• {name}: 🪙 {coins}" for name, coins in ranking[:5]]),
                    inline=False
                )
            
            embed.set_footer(text="Use /ajudamoedas para ver todos os comandos")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao verificar saldo: {e}")
            await interaction.response.send_message(
                "❌ Erro ao verificar saldo!",
                ephemeral=True
            )
    
    @app_commands.command(name="enviarmoedas", description="Enviar moedas para outro usuário")
    @app_commands.describe(usuario="Usuário que receberá as moedas", quantidade="Quantidade de moedas")
    async def enviarmoedas(self, interaction: discord.Interaction, usuario: discord.Member, quantidade: int):
        """Enviar moedas para outro usuário"""
        
        sender_id = str(interaction.user.id)
        receiver_id = str(usuario.id)
        sender_name = interaction.user.name
        receiver_name = usuario.name
        
        logger.info(f"Comando /enviarmoedas usado por {sender_name} para {receiver_name}: {quantidade}")
        
        if quantidade <= 0:
            await interaction.response.send_message(
                "❌ Quantidade deve ser maior que 0!",
                ephemeral=True
            )
            return
        
        if sender_id == receiver_id:
            await interaction.response.send_message(
                "❌ Você não pode enviar moedas para si mesmo!",
                ephemeral=True
            )
            return
        
        try:
            # Verificar saldo do remetente
            sender_balance = CoinsService.get_balance(sender_id)
            
            if sender_balance < quantidade:
                embed = discord.Embed(
                    title="❌ Saldo Insuficiente",
                    description=f"Você tem apenas 🪙 {sender_balance} moedas!",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Realizar transferência
            success = CoinsService.transfer_coins(sender_id, receiver_id, quantidade)
            
            if success:
                embed = discord.Embed(
                    title="💸 Transferência Realizada!",
                    description=f"**{sender_name}** enviou 🪙 {quantidade} moedas para **{receiver_name}**",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="💰 Novos Saldos",
                    value=f"**{sender_name}**: 🪙 {CoinsService.get_balance(sender_id)} moedas\n"
                          f"**{receiver_name}**: 🪙 {CoinsService.get_balance(receiver_id)} moedas",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    "❌ Erro ao realizar transferência!",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erro ao transferir moedas: {e}")
            await interaction.response.send_message(
                "❌ Erro ao transferir moedas!",
                ephemeral=True
            )
    
    @app_commands.command(name="rankingmoedas", description="Ver ranking de moedas do servidor")
    async def rankingmoedas(self, interaction: discord.Interaction):
        """Mostrar ranking de moedas"""
        
        logger.info(f"Comando /rankingmoedas usado por {interaction.user.name}")
        
        try:
            # Obter ranking do serviço
            ranking = CoinsService.get_top_balance(20)
            
            if not ranking:
                embed = discord.Embed(
                    title="💰 Ranking de Moedas",
                    description="Nenhum jogador encontrado!",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Criar embed com ranking
            embed = discord.Embed(
                title="💰 Ranking de Moedas",
                description="Jogadores mais ricos do servidor",
                color=discord.Color.gold()
            )
            
            # Adicionar jogadores ao embed
            for i, (name, coins) in enumerate(ranking[:15], 1):
                # Emoji por posição
                if i == 1:
                    medal = "🥇"
                elif i == 2:
                    medal = "🥈"
                elif i == 3:
                    medal = "🥉"
                else:
                    medal = f"#{i}"
                
                embed.add_field(
                    name=f"{medal} {name}",
                    value=f"🪙 {coins} moedas",
                    inline=False
                )
            
            embed.set_footer(text=f"Total de jogadores: {len(ranking)}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao mostrar ranking de moedas: {e}")
            await interaction.response.send_message(
                "❌ Erro ao buscar ranking de moedas!",
                ephemeral=True
            )
    
    @app_commands.command(name="ajudamoedas", description="Ver ajuda sobre comandos de moedas")
    async def ajudamoedas(self, interaction: discord.Interaction):
        """Mostrar ajuda dos comandos de moedas"""
        
        embed = discord.Embed(
            title="💰 Ajuda - Sistema de Moedas",
            description="Todos os comandos relacionados a moedas",
            color=discord.Color.blue()
        )
        
        commands_info = [
            ("💰 /saldo", "Verificar seu saldo de moedas"),
            ("💸 /enviarmoedas", "Enviar moedas para outro usuário"),
            ("🏆 /rankingmoedas", "Ver ranking dos mais ricos"),
            ("🎯 /ganharmoedas", "Ganhar moedas (admin)"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.add_field(
            name="💡 Dicas",
            value="• Participe de torneios para ganhar moedas\n"
                  "• Use moedas na loja virtual\n"
                  "• Troque com outros jogadores",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup dos comandos de moedas"""
    await bot.add_cog(CoinsCommands(bot))
