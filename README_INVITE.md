# Gerador de Convite - BattleDex Arena Bot

Este script permite gerar URLs de convite personalizadas para o bot Discord do BattleDex Arena.

## 🚀 Como Usar

### Opção 1: Execução Interativa (Recomendado)

```bash
python create_invite.py
```

O script irá perguntar:
- ID do aplicativo Discord (Application ID)
- Tipo de convite (Básico ou Admin)

### Opção 2: Configurar no .env

Adicione ao seu arquivo `.env`:
```env
DISCORD_BOT_ID=345974040768282637
```

Depois execute:
```bash
python create_invite.py
```

## 📋 Tipos de Convite

### 🟢 Convite Básico
**Ideal para:** Usuários normais, servidores de comunidade

**Permissões:**
- ✅ Send Messages
- ✅ Read Message History  
- ✅ Embed Links
- ✅ Use Application Commands

### 🔵 Convite Admin
**Ideal para:** Administradores, servidores privados

**Permissões básicas +:**
- ✅ Manage Messages
- ✅ Manage Server
- ✅ Kick Members
- ✅ Ban Members

## 🎯 Comandos Disponíveis

Após instalar o bot, estes comandos estarão disponíveis:

- **`/showranking`** - Mostrar ranking ELO (todos podem usar)
- **`/addplayer`** - Adicionar jogador (apenas admins)
- **`/delplayer`** - Remover jogador (apenas admins)
- **`/resetelo`** - Resetar ELO individual (apenas admins)
- **`/reseteloall`** - Resetar todos os ELOs (apenas admins)

## 📝 Instruções para Usuários

1. **Copie a URL** gerada pelo script
2. **Cole no navegador**
3. **Selecione o servidor Discord** onde deseja adicionar o bot
4. **Autorize o bot** com as permissões solicitadas
5. **Espere 1-2 minutos** para os comandos aparecerem
6. **Teste com `/showranking`**

## 🔧 Como Obter o Application ID

1. Vá para [Discord Developer Portal](https://discord.com/developers/applications)
2. Selecione sua aplicação
3. O **Application ID** está na página "General Information"
4. Copie o ID numérico

## 🛠️ Como Usar o Script

### Exemplo de execução:

```
============================================================
🤖 BattleDex Arena Bot - Gerador de Convite
============================================================

📋 Informações necessárias:
🔢 ID do Aplicativo Discord (Application ID): 345974040768282637

🔧 Configuração para o bot: 345974040768282637

📋 Tipo de convite:
1. 🟢 Básico (usuários normais)
2. 🔵 Admin (com permissões de administrador)

Escolha (1 ou 2): 1

============================================================
🔗 URLs DE CONVITE GERADAS
============================================================

🟢 URL BÁSICA (recomendada para usuários):
https://discord.com/oauth2/authorize?client_id=345974040768282637&permissions=137438756864&scope=bot%20applications.commands

🔵 URL ADMIN (com permissões extras):
https://discord.com/oauth2/authorize?client_id=345974040768282637&permissions=137439045632&scope=bot%20applications.commands
```

## 💾 Salvamento Automático

O script oferece opção para salvar as URLs em um arquivo:
- Nome: `discord_invite_[CLIENT_ID].txt`
- Formato: Arquivo de texto com URLs e instruções

## 🔍 Solução de Problemas

### Comandos não aparecem após instalar?

1. **Espere 1-2 minutos** (sincronização pode demorar)
2. **Reinicie o Discord** (Ctrl+R)
3. **Verifique permissões** em Server Settings > Integrations
4. **Remova e re-adicione** o bot se necessário

### Bot não responde aos comandos?

1. **Verifique logs** do bot Docker
2. **Confirme se o bot está online**
3. **Verifique se o usuário tem permissões** (para comandos admin)

## 📞 Suporte

Se precisar de ajuda:
- Verifique os logs do bot: `docker logs battledex-arena-discord`
- Confirme a configuração do `.env`
- Teste com o comando `/showranking` primeiro

---

**BattleDex Arena Bot** 🤖  
Ranking ELO para competições de BattleDex
