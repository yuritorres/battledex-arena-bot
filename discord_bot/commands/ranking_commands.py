"""
BattleDex Arena - Discord Ranking Commands
Comandos de ranking para Discord usando serviços compartilhados
"""

import discord
from discord import app_commands
import logging

from shared.ranking_service import RankingService

logger = logging.getLogger(__name__)

from discord.ext import commands

class RankingCommands(commands.Cog):
    """Commands para ranking do Discord"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="addplayer", description="Adicionar jogador ao ranking")
    @app_commands.describe(nome="Nome do jogador a ser adicionado")
    async def addplayer(self, interaction: discord.Interaction, nome: str):
        """Adicionar jogador ao ranking (Admin only)"""
        
        # Verificar se é admin
        if not self.bot.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True
            )
            return
        
        # Adicionar jogador
        success = RankingService.add_player(nome)
        
        if success:
            embed = discord.Embed(
                title="✅ Jogador Adicionado",
                description=f"Jogador **{nome}** adicionado com sucesso!",
                color=discord.Color.green()
            )
            embed.add_field(name="ELO Inicial", value="1000")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ Erro ao adicionar jogador!",
                ephemeral=True
            )
    
    @app_commands.command(name="delplayer", description="Remover jogador do ranking")
    @app_commands.describe(nome="Nome do jogador a ser removido")
    async def delplayer(self, interaction: discord.Interaction, nome: str):
        """Remover jogador do ranking (Admin only)"""
        
        # Verificar se é admin
        if not self.bot.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True
            )
            return
        
        # Verificar se jogador existe
        if not RankingService.player_exists(nome):
            await interaction.response.send_message(
                f"❌ Jogador **{nome}** não encontrado no ranking!",
                ephemeral=True
            )
            return
        
        # Remover jogador
        success = RankingService.remove_player(nome)
        
        if success:
            embed = discord.Embed(
                title="✅ Jogador Removido",
                description=f"Jogador **{nome}** removido com sucesso!",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ Erro ao remover jogador!",
                ephemeral=True
            )
    
    @app_commands.command(name="showranking", description="Mostrar ranking atual")
    async def showranking(self, interaction: discord.Interaction):
        """Mostrar ranking atual"""
        
        ranking_text = RankingService.get_ranking()
        
        embed = discord.Embed(
            title="📊 Ranking BF 🔰",
            description=ranking_text,
            color=discord.Color.blue()
        )
        embed.set_thumbnail(
            url="https://cdn-icons-png.flaticon.com/512/3408/3408593.png"
        )
        embed.set_footer(text="BattleDex Arena - Ranking ELO")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="resetelo", description="Resetar ELO de um jogador")
    @app_commands.describe(nome="Nome do jogador")
    async def resetelo(self, interaction: discord.Interaction, nome: str):
        """Resetar ELO de um jogador (Admin only)"""
        
        # Verificar se é admin
        if not self.bot.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True
            )
            return
        
        # Verificar se jogador existe
        if not RankingService.player_exists(nome):
            await interaction.response.send_message(
                f"❌ Jogador **{nome}** não encontrado no ranking!",
                ephemeral=True
            )
            return
        
        # Resetar ELO
        success = RankingService.reset_elo(nome)
        
        if success:
            embed = discord.Embed(
                title="🔄 ELO Resetado",
                description=f"ELO de **{nome}** foi resetado para 1000!",
                color=discord.Color.yellow()
            )
            embed.add_field(name="Novo ELO", value="1000")
            embed.add_field(name="Vitórias", value="0")
            embed.add_field(name="Derrotas", value="0")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ Erro ao resetar ELO!",
                ephemeral=True
            )
    
    @app_commands.command(name="reseteloall", description="Resetar ELO de todos os jogadores")
    async def reseteloall(self, interaction: discord.Interaction):
        """Resetar ELO de todos os jogadores (Admin only)"""
        
        # Verificar se é admin
        if not self.bot.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True
            )
            return
        
        # Confirmar ação
        embed = discord.Embed(
            title="⚠️ Confirmar Reset Total",
            description="Tem certeza que deseja resetar o ELO de TODOS os jogadores?",
            color=discord.Color.red()
        )
        embed.add_field(name="Ação", value="Resetar todos os ELOs para 1000")
        embed.add_field(name="Impacto", value="Todas as vitórias e derrotas serão zeradas")
        
        view = ConfirmResetView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ConfirmResetView(discord.ui.View):
    """View para confirmação de reset total"""
    
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=30.0)
        self.bot = bot
        self.value = None
    
    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Confirmar reset"""
        
        success = RankingService.reset_all_elo()
        
        if success:
            embed = discord.Embed(
                title="✅ Reset Completo",
                description="Todos os ELOs foram resetados para 1000!",
                color=discord.Color.green()
            )
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            await interaction.response.edit_message(
                content="❌ Erro ao resetar ELOs!",
                view=None
            )
        
        self.value = True
        self.stop()
    
    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cancelar reset"""
        
        embed = discord.Embed(
            title="❌ Cancelado",
            description="Operação de reset foi cancelada.",
            color=discord.Color.grey()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        
        self.value = False
        self.stop()

async def setup(bot: commands.Bot):
    """Setup dos comandos de ranking"""
    await bot.add_cog(RankingCommands(bot))
