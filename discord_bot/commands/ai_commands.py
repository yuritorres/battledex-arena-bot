"""
Comandos de IA para Discord
"""

import discord
from discord import app_commands
import logging
import asyncio

from shared.ai_service import AIService

logger = logging.getLogger(__name__)

from discord.ext import commands

class AICommands(commands.Cog):
    """Commands para sistema de IA"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="perguntar", description="Fazer uma pergunta para a IA sobre BattleDex")
    @app_commands.describe(pergunta="Sua pergunta sobre BattleDex")
    async def perguntar(self, interaction: discord.Interaction, pergunta: str):
        """Fazer uma pergunta para a IA"""
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        
        logger.info(f"Comando /perguntar usado por {username}: {pergunta}")
        
        try:
            # Indicar que está processando
            await interaction.response.defer()
            
            # Obter resposta da IA
            ai_response = AIService.ask_question(pergunta, user_id)
            
            if not ai_response:
                await interaction.followup.send(
                    "❌ Não consegui obter resposta da IA no momento!",
                    ephemeral=True
                )
                return
            
            # Criar embed com a resposta
            embed = discord.Embed(
                title="🤖 IA BattleDex",
                description=f"**Pergunta de {username}:**\n*{pergunta}*",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="💭 Resposta da IA",
                value=ai_response,
                inline=False
            )
            
            embed.set_footer(text="Resposta gerada por IA | Pode conter erros")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao processar pergunta: {e}")
            await interaction.followup.send(
                "❌ Erro ao processar sua pergunta!",
                ephemeral=True
            )
    
    @app_commands.command(name="analisarjogador", description="Analisar um jogador com IA")
    @app_commands.describe(nome="Nome do jogador para analisar")
    async def analisarjogador(self, interaction: discord.Interaction, nome: str):
        """Analisar estatísticas de um jogador com IA"""
        
        username = interaction.user.name
        
        logger.info(f"Comando /analisarjogador usado por {username}: {nome}")
        
        try:
            # Indicar que está processando
            await interaction.response.defer()
            
            # Obter dados do jogador
            from shared.ranking_service import RankingService
            player_stats = RankingService.get_player_stats(nome)
            
            if not player_stats:
                await interaction.followup.send(
                    f"❌ Jogador **{nome}** não encontrado no ranking!",
                    ephemeral=True
                )
                return
            
            elo, vitorias, derrotas = player_stats
            
            # Preparar prompt para IA
            prompt = f"""
            Analise o jogador {nome} com base nas seguintes estatísticas:
            - ELO atual: {elo}
            - Vitórias: {vitorias}
            - Derrotas: {derrotas}
            
            Forneça uma análise detalhada incluindo:
            1. Nível do jogador (iniciante, intermediário, avançado)
            2. Pontos fortes
            3. Áreas de melhoria
            4. Dicas para melhorar o desempenho
            """
            
            # Obter análise da IA
            ai_analysis = AIService.ask_question(prompt, str(interaction.user.id))
            
            if not ai_analysis:
                await interaction.followup.send(
                    "❌ Não consegui gerar análise no momento!",
                    ephemeral=True
                )
                return
            
            # Criar embed com a análise
            embed = discord.Embed(
                title="📊 Análise de Jogador",
                description=f"Análise de **{nome}** por IA",
                color=discord.Color.purple()
            )
            
            # Adicionar estatísticas básicas
            win_rate = (vitorias / (vitorias + derrotas) * 100) if (vitorias + derrotas) > 0 else 0
            
            embed.add_field(
                name="📈 Estatísticas",
                value=f"🏆 ELO: {elo}\n"
                      f"✅ Vitórias: {vitorias}\n"
                      f"❌ Derrotas: {derrotas}\n"
                      f"📊 Taxa de Vitória: {win_rate:.1f}%",
                inline=False
            )
            
            embed.add_field(
                name="🤖 Análise da IA",
                value=ai_analysis,
                inline=False
            )
            
            embed.set_footer(text="Análise gerada por IA | Baseada nas estatísticas disponíveis")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao analisar jogador: {e}")
            await interaction.followup.send(
                "❌ Erro ao analisar jogador!",
                ephemeral=True
            )
    
    @app_commands.command(name="dica", description="Obter uma dica de BattleDex")
    @app_commands.describe(topico="Tópico da dica (ataque, defesa, estratégia, etc.)")
    async def dica(self, interaction: discord.Interaction, topico: str = "geral"):
        """Obter uma dica de BattleDex"""
        
        username = interaction.user.name
        
        logger.info(f"Comando /dica usado por {username}: {topico}")
        
        try:
            # Indicar que está processando
            await interaction.response.defer()
            
            # Preparar prompt para IA
            prompt = f"""
            Forneça uma dica útil de BattleDex sobre o tema "{topico}".
            A dica deve ser:
            1. Prática e aplicável
            2. Fácil de entender
            3. Útil para jogadores de diferentes níveis
            4. Específica para o tema solicitado
            """
            
            # Obter dica da IA
            ai_tip = AIService.ask_question(prompt, str(interaction.user.id))
            
            if not ai_tip:
                await interaction.followup.send(
                    "❌ Não consegui gerar dica no momento!",
                    ephemeral=True
                )
                return
            
            # Criar embed com a dica
            embed = discord.Embed(
                title="💡 Dica de BattleDex",
                description=f"Dica sobre **{topico}**",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="🎯 Dica da IA",
                value=ai_tip,
                inline=False
            )
            
            embed.add_field(
                name="💭 Como usar esta dica",
                value="Pratique esta dica em suas próximas batalhas para ver melhores resultados!",
                inline=False
            )
            
            embed.set_footer(text=f"Solicitada por {username} | Dica gerada por IA")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao gerar dica: {e}")
            await interaction.followup.send(
                "❌ Erro ao gerar dica!",
                ephemeral=True
            )
    
    @app_commands.command(name="ajudaia", description="Ver ajuda sobre comandos de IA")
    async def ajudaia(self, interaction: discord.Interaction):
        """Mostrar ajuda dos comandos de IA"""
        
        embed = discord.Embed(
            title="🤖 Ajuda - Sistema de IA",
            description="Todos os comandos relacionados à IA",
            color=discord.Color.blue()
        )
        
        commands_info = [
            ("❓ /perguntar", "Fazer perguntas sobre BattleDex"),
            ("📊 /analisarjogador", "Analisar estatísticas de um jogador"),
            ("💡 /dica", "Obter dicas de BattleDex"),
            ("🤖 /ajudaia", "Ver esta ajuda"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.add_field(
            name="⚠️ Importante",
            value="• As respostas são geradas por IA e podem conter erros\n"
                  "• Use as informações como referência, não como regra absoluta\n"
                  "• Para informações precisas, consulte fontes oficiais",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup dos comandos de IA"""
    await bot.add_cog(AICommands(bot))
