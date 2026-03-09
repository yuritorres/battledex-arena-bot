"""
Gerador de Convite para BattleDex Arena Bot
Este script cria URLs de convite personalizadas para o bot Discord
"""

import os
import sys
from dotenv import load_dotenv

def create_invite_url(client_id: str, include_admin_perms: bool = True) -> str:
    """Criar URL de convite com permissões configuradas"""
    
    # Permissões básicas necessárias
    base_permissions = {
        "Send Messages": 0x800,
        "Read Message History": 0x10000,
        "Embed Links": 0x4000,
        "Use Application Commands": 0x2000000000,
    }
    
    # Permissões admin (opcionais)
    admin_permissions = {
        "Manage Messages": 0x2000,
        "Manage Server": 0x20,
        "Kick Members": 0x2,
        "Ban Members": 0x4,
    }
    
    # Combinar permissões
    all_permissions = base_permissions.copy()
    if include_admin_perms:
        all_permissions.update(admin_permissions)
    
    # Calcular bitmask
    permission_bitmask = sum(all_permissions.values())
    
    # Criar URL
    scopes = ["bot", "applications.commands"]
    scope_param = "%20".join(scopes)
    
    return f"https://discord.com/oauth2/authorize?client_id={client_id}&permissions={permission_bitmask}&scope={scope_param}"

def main():
    """Função principal - interface para usuários"""
    
    print("=" * 60)
    print("🤖 BattleDex Arena Bot - Gerador de Convite")
    print("=" * 60)
    
    # Tentar carregar CLIENT_ID do .env ou pedir ao usuário
    load_dotenv()
    client_id = os.getenv('DISCORD_BOT_ID')
    
    if not client_id:
        print("\n📋 Informações necessárias:")
        client_id = input("🔢 ID do Aplicativo Discord (Application ID): ").strip()
    
    if not client_id or not client_id.isdigit():
        print("❌ ID do aplicativo inválido!")
        return
    
    print(f"\n🔧 Configuração para o bot: {client_id}")
    
    # Perguntar tipo de convite
    print("\n📋 Tipo de convite:")
    print("1. 🟢 Básico (usuários normais)")
    print("2. 🔵 Admin (com permissões de administrador)")
    
    choice = input("\nEscolha (1 ou 2): ").strip()
    
    include_admin = choice == "2"
    
    # Gerar URLs
    basic_url = create_invite_url(client_id, include_admin_perms=False)
    admin_url = create_invite_url(client_id, include_admin_perms=True)
    
    print("\n" + "=" * 60)
    print("🔗 URLs DE CONVITE GERADAS")
    print("=" * 60)
    
    print(f"\n🟢 URL BÁSICA (recomendada para usuários):")
    print(f"{basic_url}")
    
    print(f"\n🔵 URL ADMIN (com permissões extras):")
    print(f"{admin_url}")
    
    print("\n� Permissões incluídas:")
    
    print("\n🟢 Básicas (ambas as URLs):")
    basic_perms = ["Send Messages", "Read Message History", "Embed Links", "Use Application Commands"]
    for perm in basic_perms:
        print(f"  ✅ {perm}")
    
    if include_admin:
        print("\n🔵 Adicionais (URL Admin):")
        admin_perms = ["Manage Messages", "Manage Server", "Kick Members", "Ban Members"]
        for perm in admin_perms:
            print(f"  ✅ {perm}")
    
    print("\n📝 Instruções para os usuários:")
    print("1. Copie a URL desejada")
    print("2. Cole no navegador")
    print("3. Selecione o servidor Discord")
    print("4. Autorize o bot")
    print("5. Espere 1-2 minutos para os comandos aparecerem")
    
    print("\n🎯 Comandos disponíveis após instalação:")
    commands = [
        "/showranking - Mostrar ranking ELO",
        "/addplayer - Adicionar jogador (admin)",
        "/delplayer - Remover jogador (admin)",
        "/resetelo - Resetar ELO (admin)",
        "/reseteloall - Resetar todos (admin)"
    ]
    
    for cmd in commands:
        print(f"  • {cmd}")
    
    print("\n" + "=" * 60)
    print("✅ URLs geradas com sucesso!")
    print("=" * 60)
    
    # Salvar em arquivo para fácil compartilhamento
    save_to_file = input("\n💾 Salvar URLs em arquivo? (s/n): ").strip().lower()
    
    if save_to_file == 's':
        filename = f"discord_invite_{client_id}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"BattleDex Arena Bot - URLs de Convite\n")
            f.write(f"Client ID: {client_id}\n")
            f.write(f"Gerado em: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"URL BÁSICA:\n{basic_url}\n\n")
            f.write(f"URL ADMIN:\n{admin_url}\n")
        
        print(f"💾 Salvo em: {filename}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)
