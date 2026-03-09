"""
Comandos de loja para Discord
"""

import discord
from discord import app_commands
import logging

from shared.shop_service import ShopService

logger = logging.getLogger(__name__)

from discord.ext import commands

class ShopCommands(commands.Cog):
    """Commands para sistema de loja"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="loja", description="Ver itens disponíveis na loja")
    async def loja(self, interaction: discord.Interaction):
        """Mostrar itens disponíveis na loja"""
        
        logger.info(f"Comando /loja usado por {interaction.user.name}")
        
        try:
            # Obter itens da loja
            items = ShopService.get_all_items()
            
            if not items:
                embed = discord.Embed(
                    title="🛍️ Loja BattleDex",
                    description="Nenhum item disponível no momento!",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Criar embed com itens
            embed = discord.Embed(
                title="🛍️ Loja BattleDex Arena",
                description="Itens disponíveis para compra",
                color=discord.Color.purple()
            )
            
            # Adicionar itens ao embed
            for item in items:
                name = item.get('name', 'Item Desconhecido')
                price = item.get('price', 0)
                description = item.get('description', 'Sem descrição')
                stock = item.get('stock', 0)
                
                # Status do estoque
                if stock <= 0:
                    status = "❌ ESGOTADO"
                    color = "🔴"
                elif stock <= 5:
                    status = f"⚠️ Últimas {stock} unidades"
                    color = "🟡"
                else:
                    status = f"✅ {stock} disponíveis"
                    color = "🟢"
                
                embed.add_field(
                    name=f"{color} {name}",
                    value=f"💰 Preço: 🪙 {price} moedas\n"
                          f"📝 {description}\n"
                          f"📦 {status}",
                    inline=False
                )
            
            embed.set_footer(text="Use /comprar <item> para comprar")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao mostrar loja: {e}")
            await interaction.response.send_message(
                "❌ Erro ao carregar loja!",
                ephemeral=True
            )
    
    @app_commands.command(name="comprar", description="Comprar um item da loja")
    @app_commands.describe(item="Nome do item que deseja comprar")
    async def comprar(self, interaction: discord.Interaction, item: str):
        """Comprar um item da loja"""
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        
        logger.info(f"Comando /comprar usado por {username}: {item}")
        
        try:
            # Verificar se o item existe
            item_data = ShopService.get_item(item)
            
            if not item_data:
                embed = discord.Embed(
                    title="❌ Item Não Encontrado",
                    description=f"**{item}** não está disponível na loja!",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Verificar estoque
            stock = item_data.get('stock', 0)
            if stock <= 0:
                embed = discord.Embed(
                    title="❌ Item Esgotado",
                    description=f"**{item}** está esgotado!",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Verificar saldo do usuário
            price = item_data.get('price', 0)
            user_balance = CoinsService.get_balance(user_id)
            
            if user_balance < price:
                embed = discord.Embed(
                    title="❌ Saldo Insuficiente",
                    description=f"Você precisa de 🪙 {price} moedas para comprar **{item}**!\n"
                              f"Seu saldo atual: 🪙 {user_balance} moedas",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Realizar compra
            success = ShopService.buy_item(user_id, item)
            
            if success:
                embed = discord.Embed(
                    title="🛍️ Compra Realizada!",
                    description=f"**{username}** comprou **{item}** por 🪙 {price} moedas!",
                    color=discord.Color.green()
                )
                
                embed.add_field(
                    name="💰 Novo Saldo",
                    value=f"🪙 {CoinsService.get_balance(user_id)} moedas",
                    inline=False
                )
                
                embed.add_field(
                    name="📦 Item",
                    value=f"**{item}** - {item_data.get('description', 'Sem descrição')}",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(
                    "❌ Erro ao realizar compra!",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erro ao comprar item: {e}")
            await interaction.response.send_message(
                "❌ Erro ao comprar item!",
                ephemeral=True
            )
    
    @app_commands.command(name="inventario", description="Ver seu inventário de itens")
    async def inventario(self, interaction: discord.Interaction):
        """Mostrar inventário do usuário"""
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        
        logger.info(f"Comando /inventario usado por {username}")
        
        try:
            # Obter inventário do usuário
            inventory = ShopService.get_user_inventory(user_id)
            
            if not inventory:
                embed = discord.Embed(
                    title="🎒 Inventário",
                    description=f"**{username}** não tem itens no inventário!",
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=embed)
                return
            
            # Criar embed com inventário
            embed = discord.Embed(
                title="🎒 Inventário",
                description=f"Itens de **{username}**",
                color=discord.Color.blue()
            )
            
            # Adicionar itens ao embed
            for item_name, quantity in inventory.items():
                item_data = ShopService.get_item(item_name)
                description = item_data.get('description', 'Sem descrição') if item_data else 'Item desconhecido'
                
                embed.add_field(
                    name=f"📦 {item_name}",
                    value=f"Quantidade: {quantity}\n"
                          f"📝 {description}",
                    inline=False
                )
            
            embed.set_footer(text="Use /loja para ver mais itens")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Erro ao mostrar inventário: {e}")
            await interaction.response.send_message(
                "❌ Erro ao carregar inventário!",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    """Setup dos comandos de loja"""
    await bot.add_cog(ShopCommands(bot))
