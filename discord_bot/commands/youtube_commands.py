"""
Comandos de YouTube para Discord
Funciona igual ao Telegram notifier
"""

import discord
from discord import app_commands
import logging
import os
import json
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

from discord.ext import commands

class YouTubeCommands(commands.Cog):
    """Commands para YouTube no Discord"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Canal do Discord para notificações (via variável de ambiente)
        self.youtube_channel_id = os.getenv('DISCORD_YOUTUBE_CHANNEL_ID', '')
    
    @app_commands.command(name="youtube", description="Ver informações do canal YouTube")
    async def youtube(self, interaction: discord.Interaction):
        """Mostrar informações do canal YouTube configurado"""
        
        logger.info(f"Comando /youtube usado por {interaction.user.name}")
        
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        if not channel_id:
            embed = discord.Embed(
                title="❌ YouTube Não Configurado",
                description="O canal YouTube não está configurado no bot.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📺 YouTube Notifier",
            description="Sistema de notificações de vídeos do YouTube",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🔗 Canal ID",
            value=f"`{channel_id}`",
            inline=False
        )
        
        embed.add_field(
            name="💬 Canal Discord",
            value=f"<#{self.youtube_channel_id}>",
            inline=False
        )
        
        embed.add_field(
            name="📋 Status",
            value="🟢 Ativo e monitorando novos vídeos",
            inline=False
        )
        
        embed.add_field(
            name="🔧 Comandos",
            value="• `/youtube` - Ver informações\n"
                  "• `/ultimovideo` - Ver último vídeo\n"
                  "• `/testarnotificacao` - Testar notificação",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ultimovideo", description="Ver o último vídeo do canal YouTube")
    async def ultimovideo(self, interaction: discord.Interaction):
        """Mostrar o último vídeo do canal YouTube"""
        
        logger.info(f"Comando /ultimovideo usado por {interaction.user.name}")
        
        try:
            await interaction.response.defer()
            
            channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
            if not channel_id:
                await interaction.followup.send("❌ YouTube não configurado!", ephemeral=True)
                return
            
            # Importar o serviço do YouTube
            from services.youtube_notifier import _fetch_feed_entries, FEED_TEMPLATE
            
            feed_url = FEED_TEMPLATE.format(channel_id=channel_id)
            entries = await _fetch_feed_entries(feed_url)
            
            if not entries:
                embed = discord.Embed(
                    title="❌ Nenhum Vídeo",
                    description="Não foi possível encontrar vídeos no canal.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Pegar o vídeo mais recente
            latest = entries[0]
            title = latest.get('title', 'Sem título')
            link = latest.get('link', '#')
            published = latest.get('published', '')
            
            embed = discord.Embed(
                title="🎬 Último Vídeo",
                description=f"**{title}**",
                url=link,
                color=discord.Color.red()
            )
            
            embed.add_field(
                name="📅 Data de Publicação",
                value=published or "Data não disponível",
                inline=False
            )
            
            embed.add_field(
                name="🔗 Link",
                value=f"[Assistir agora]({link})",
                inline=False
            )
            
            embed.set_thumbnail(
                url="https://img.youtube.com/vi/" + link.split('v=')[-1].split('&')[0] + "/maxresdefault.jpg"
            )
            
            embed.set_footer(text="Canal YouTube - BattleDex Arena")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao buscar último vídeo: {e}")
            await interaction.followup.send(
                "❌ Erro ao buscar informações do YouTube!",
                ephemeral=True
            )
    
    @app_commands.command(name="testarnotificacao", description="Testar notificação do YouTube")
    async def testarnotificacao(self, interaction: discord.Interaction):
        """Testar sistema de notificação do YouTube"""
        
        logger.info(f"Comando /testarnotificacao usado por {interaction.user.name}")
        
        # Verificar se é admin
        if not self.bot.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True
            )
            return
        
        try:
            await interaction.response.defer()
            
            # Usar o notificador do bot
            success, message = await self.bot.youtube_notifier.send_test_notification()
            
            if success:
                await interaction.followup.send(
                    f"✅ {message} para <#{self.youtube_channel_id}>!",
                    ephemeral=True
                )
            else:
                await interaction.followup.send(
                    f"❌ Erro ao testar notificação: {message}",
                    ephemeral=True
                )
            
        except Exception as e:
            logger.error(f"Erro ao testar notificação: {e}")
            await interaction.followup.send(
                "❌ Erro ao enviar teste de notificação!",
                ephemeral=True
            )
    
    @app_commands.command(name="canalyoutube", description="Configurar canal para notificações YouTube")
    @app_commands.describe(canal="Canal do Discord para notificações")
    async def canalyoutube(self, interaction: discord.Interaction, canal: discord.TextChannel):
        """Configurar canal para notificações YouTube (admin only)"""
        
        # Verificar se é admin
        if not self.bot.is_admin(interaction.user):
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True
            )
            return
        
        logger.info(f"Comando /canalyoutube usado por {interaction.user.name}: {channel.name}")
        
        # Atualizar canal
        self.youtube_channel_id = str(canal.id)
        
        embed = discord.Embed(
            title="✅ Canal YouTube Atualizado",
            description=f"Canal para notificações YouTube configurado!",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📺 Novo Canal",
            value=f"<#{canal.id}> ({canal.name})",
            inline=False
        )
        
        embed.add_field(
            name="🔧 ID do Canal",
            value=f"`{canal.id}`",
            inline=False
        )
        
        embed.add_field(
            name="📋 Próximos Passos",
            value="1. Use `/testarnotificacao` para testar\n"
                  "2. Configure YOUTUBE_CHANNEL_ID no .env\n"
                  "3. Reinicie o bot para ativar o monitoramento",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup dos comandos de YouTube"""
    await bot.add_cog(YouTubeCommands(bot))
