"""
Teste simples para verificar comandos Discord
"""

import asyncio
import os
from dotenv import load_dotenv
from discord_bot.discord_bot import create_discord_bot

async def test_commands():
    """Testar carregamento de comandos"""
    
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Criar bot
    bot = create_discord_bot()
    
    # Carregar comandos manualmente
    try:
        from discord_bot.commands.ranking_commands import setup
        await setup(bot)
        print("✅ Comandos carregados com sucesso!")
        
        # Listar comandos na árvore
        commands = list(bot.tree.walk_commands())
        print(f"📋 Total de comandos: {len(commands)}")
        
        for cmd in commands:
            print(f"  - /{cmd.name}: {cmd.description}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_commands())
