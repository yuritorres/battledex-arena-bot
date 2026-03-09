# Docker Setup - Telegram + Discord

## Opções de Deploy

### Opção 1: Containers Separados (Recomendado)

Use `docker-compose.yml` para rodar Telegram e Discord em containers separados:

```bash
# Construir e iniciar ambos os bots
docker-compose up -d --build

# Ver logs
docker-compose logs -f

# Parar
docker-compose down
```

**Serviços criados:**
- `battledex-arena-telegram` - Bot Telegram
- `battledex-arena-discord` - Bot Discord
- `battledex-network` - Rede compartilhada

### Opção 2: Container Único

Use `docker-compose.both.yml` para rodar ambos os bots em um único container:

```bash
# Construir e iniciar
docker-compose -f docker-compose.both.yml up -d --build

# Ver logs
docker-compose -f docker-compose.both.yml logs -f

# Parar
docker-compose -f docker-compose.both.yml down
```

## Configuração

### 1. Variáveis de Ambiente

Configure seu `.env` com ambos os tokens:

```env
# Telegram
TELEGRAM_TOKEN=seu_token_telegram_aqui
ADMINS=123456789

# Discord
DISCORD_BOT_TOKEN=seu_token_discord_aqui
DISCORD_ADMIN_ROLE_ID=123456789012345678
DISCORD_GUILD_ID=123456789012345678

# IA
OPENAI_API_KEY=sk-xxxxx
GEMINI_API_KEY=gemini-xxxxx
```

### 2. IDs Discord

Para obter os IDs Discord:

**Guild ID (Server ID):**
1. Ative Developer Mode em Discord > Configurações > Avançado
2. Clique com botão direito no ícone do servidor > "Copiar Server ID"

**Admin Role ID:**
1. Vá em Server Settings > Roles
2. Clique na role de admin e copie o ID da URL

**Channel IDs (opcional):**
1. Clique com botão direito no canal > "Copy Channel ID"

### 3. Permissões Discord

Crie uma role "Admin" no servidor Discord com:
- Gerenciar servidor
- Gerenciar canais
- Gerenciar mensagens
- Usar comandos slash

## Comandos

### Telegram (existententes)
- `/addplayer <nome>` - Adicionar jogador
- `/showranking` - Mostrar ranking
- `/ia <mensagem>` - Perguntar à IA

### Discord (novos)
- `/addplayer <nome>` - Adicionar jogador
- `/delplayer <nome>` - Remover jogador
- `/showranking` - Mostrar ranking
- `/resetelo <nome>` - Resetar ELO
- `/reseteloall` - Resetar todos

## Banco de Dados

Ambos os bots compartilham a mesma pasta `storage/`:
- `rankingbf.db` - Ranking ELO
- `coins.db` - Moedas
- `inventario.db` - Inventário

## Troubleshooting

### Bot Discord não conecta
```bash
# Ver logs do container Discord
docker logs battledex-arena-discord

# Verificar token
echo $DISCORD_BOT_TOKEN
```

### Permissões negadas
1. Verifique se `DISCORD_ADMIN_ROLE_ID` está correto
2. Confirme que o usuário tem a role configurada

### Comandos não aparecem
1. Reinicie o bot Discord
2. Verifique se o bot tem permissões de "Use Application Commands"
3. Sincronize comandos manualmente se necessário

## Monitoramento

```bash
# Status dos containers
docker-compose ps

# Logs em tempo real
docker-compose logs -f telegram-bot
docker-compose logs -f discord-bot

# Reiniciar serviço específico
docker-compose restart discord-bot
```

## Backup

O volume `./storage` é persistente. Para backup:

```bash
# Parar bots
docker-compose down

# Backup da pasta storage
tar -czf battledex-backup-$(date +%Y%m%d).tar.gz storage/

# Reiniciar
docker-compose up -d
```
