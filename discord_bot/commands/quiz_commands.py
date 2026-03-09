"""
Comandos de quiz para Discord
"""

import discord
from discord import app_commands
import logging
import asyncio

from shared.quiz_service import QuizService

logger = logging.getLogger(__name__)

from discord.ext import commands

class QuizCommands(commands.Cog):
    """Commands para sistema de quiz"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_quizzes = {}  # user_id -> quiz_data
    
    @app_commands.command(name="quiz", description="Iniciar um quiz de BattleDex")
    async def quiz(self, interaction: discord.Interaction):
        """Iniciar um novo quiz"""
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        
        logger.info(f"Comando /quiz usado por {username}")
        
        if user_id in self.active_quizzes:
            await interaction.response.send_message(
                "❌ Você já tem um quiz em andamento! Use /responder <resposta> para continuar.",
                ephemeral=True
            )
            return
        
        try:
            # Obter pergunta do quiz
            quiz_data = QuizService.get_random_question()
            
            if not quiz_data:
                await interaction.response.send_message(
                    "❌ Nenhuma pergunta disponível no momento!",
                    ephemeral=True
                )
                return
            
            # Armazenar quiz ativo
            self.active_quizzes[user_id] = {
                'question': quiz_data,
                'start_time': asyncio.get_event_loop().time()
            }
            
            question_text = quiz_data.get('question', 'Pergunta não disponível')
            options = quiz_data.get('options', [])
            correct_answer = quiz_data.get('correct_answer', '')
            
            # Criar embed com a pergunta
            embed = discord.Embed(
                title="🎯 Quiz BattleDex",
                description=f"**Pergunta:** {question_text}",
                color=discord.Color.blue()
            )
            
            # Adicionar opções
            for i, option in enumerate(options, 1):
                embed.add_field(
                    name=f"Opção {i}",
                    value=option,
                    inline=False
                )
            
            embed.add_field(
                name="💡 Como responder",
                value="Use `/responder <número>` (ex: `/responder 2` para a opção 2)",
                inline=False
            )
            
            embed.set_footer(text="⏱️ Você tem 30 segundos para responder!")
            
            await interaction.response.send_message(embed=embed)
            
            # Agendar timeout (não implementado aqui para simplicidade)
            
        except Exception as e:
            logger.error(f"Erro ao iniciar quiz: {e}")
            await interaction.response.send_message(
                "❌ Erro ao iniciar quiz!",
                ephemeral=True
            )
    
    @app_commands.command(name="responder", description="Responder a uma pergunta de quiz")
    @app_commands.describe(resposta="Número da opção (1, 2, 3, etc.)")
    async def responder(self, interaction: discord.Interaction, resposta: int):
        """Responder a uma pergunta de quiz ativo"""
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        
        logger.info(f"Comando /responder usado por {username}: {resposta}")
        
        if user_id not in self.active_quizzes:
            await interaction.response.send_message(
                "❌ Você não tem um quiz ativo! Use `/quiz` para iniciar.",
                ephemeral=True
            )
            return
        
        try:
            quiz_data = self.active_quizzes[user_id]
            question = quiz_data['question']
            
            options = question.get('options', [])
            correct_answer = question.get('correct_answer', '')
            
            if resposta < 1 or resposta > len(options):
                await interaction.response.send_message(
                    f"❌ Resposta inválida! Escolha um número entre 1 e {len(options)}.",
                    ephemeral=True
                )
                return
            
            # Verificar resposta
            user_answer = options[resposta - 1]
            is_correct = user_answer.lower() == correct_answer.lower()
            
            # Remover quiz ativo
            del self.active_quizzes[user_id]
            
            # Criar embed com resultado
            if is_correct:
                embed = discord.Embed(
                    title="✅ Resposta Correta!",
                    description=f"Parabéns **{username}**! Você acertou!",
                    color=discord.Color.green()
                )
                
                # Adicionar recompensa (se implementado)
                embed.add_field(
                    name="🎯 Recompensa",
                    value="🪙 50 moedas ganhas!",
                    inline=False
                )
                
                # Adicionar moedas (se implementado)
                try:
                    from shared.coins_service import CoinsService
                    CoinsService.add_coins(user_id, 50)
                except:
                    pass  # Ignorar erro se o serviço não estiver disponível
                
            else:
                embed = discord.Embed(
                    title="❌ Resposta Incorreta!",
                    description=f"A resposta correta era: **{correct_answer}**",
                    color=discord.Color.red()
                )
                
                embed.add_field(
                    name="💭 Sua resposta",
                    value=user_answer,
                    inline=False
                )
            
            # Adicionar detalhes da pergunta
            embed.add_field(
                name="📝 Pergunta",
                value=question.get('question', 'Pergunta não disponível'),
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao responder quiz: {e}")
            await interaction.response.send_message(
                "❌ Erro ao processar resposta!",
                ephemeral=True
            )
    
    @app_commands.command(name="rankingquiz", description="Ver ranking de quiz")
    async def rankingquiz(self, interaction: discord.Interaction):
        """Mostrar ranking de quiz"""
        
        logger.info(f"Comando /rankingquiz usado por {interaction.user.name}")
        
        try:
            # Obter ranking de quiz (se implementado)
            # Por enquanto, mostrar mensagem informativa
            
            embed = discord.Embed(
                title="🏆 Ranking de Quiz",
                description="Ranking de jogadores com melhor desempenho nos quizzes!",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="📊 Estatísticas",
                value="• Total de quizzes realizados: 0\n"
                      "• Taxa de acerto média: 0%\n"
                      "• Jogadores ativos: 0",
                inline=False
            )
            
            embed.add_field(
                name="💡 Dicas",
                value="• Participe de quizzes para ganhar moedas\n"
                      "• Responda rapidamente para bônus\n"
                      "• Estude as perguntas para melhorar seu score",
                inline=False
            )
            
            embed.set_footer(text="Ranking em desenvolvimento - Participe dos quizzes!")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao mostrar ranking de quiz: {e}")
            await interaction.response.send_message(
                "❌ Erro ao carregar ranking de quiz!",
                ephemeral=True
            )
    
    @app_commands.command(name="ajudaquiz", description="Ver ajuda sobre comandos de quiz")
    async def ajudaquiz(self, interaction: discord.Interaction):
        """Mostrar ajuda dos comandos de quiz"""
        
        embed = discord.Embed(
            title="🎯 Ajuda - Sistema de Quiz",
            description="Todos os comandos relacionados a quizzes",
            color=discord.Color.blue()
        )
        
        commands_info = [
            ("🎯 /quiz", "Iniciar um novo quiz de BattleDex"),
            ("💬 /responder", "Responder a uma pergunta de quiz"),
            ("🏆 /rankingquiz", "Ver ranking de jogadores"),
            ("💡 /ajudaquiz", "Ver esta ajuda"),
        ]
        
        for cmd, desc in commands_info:
            embed.add_field(name=cmd, value=desc, inline=False)
        
        embed.add_field(
            name="🎮 Como Funciona",
            value="1. Use `/quiz` para iniciar\n"
                  "2. Leia a pergunta e as opções\n"
                  "3. Use `/responder <número>` para responder\n"
                  "4. Ganhe moedas se acertar!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup dos comandos de quiz"""
    await bot.add_cog(QuizCommands(bot))
