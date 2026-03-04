# BattleDex Arena — Bot Telegram (Ranking + Gemini IA)

Este projeto contém um bot para Telegram voltado para a comunidade de batalhas estilo Pokémon Showdown. Ele gerencia ranking de jogadores (ELO, vitórias, derrotas) e integra respostas por IA (Gemini/Google Generative AI) via comando `/ia`.

## Funcionalidades
- Ranking de jogadores (adicionar, remover, mostrar ranking, resetar ELO)
- Comando `/ia <mensagem>`: responde usando a IA Gemini
- Comandos `/backup` e `/restore` exclusivos para administradores, com envio privado do arquivo compactado
- **Notificações automáticas de novos vídeos do YouTube** no grupo configurado assim que o feed do canal for atualizado
- Banco de dados SQLite local
- Configuração via arquivo `.env`
- Pronto para rodar em Docker

## Como usar

### 1. Clone o projeto

```
git clone <repo-url>
cd battledex-arena-bot
```

### 2. Configure o arquivo `.env`

Crie um arquivo `.env` na pasta `battledex-arena-bot` com (exemplo):
```
GEMINI_API_KEY=SuaChaveGeminiAqui
OPENAI_API_KEY=SuaChaveOpenAIAqui
TELEGRAM_TOKEN=SeuTokenTelegramAqui
ADMINS=123456789,987654321

# IDs do grupo/tópico
CHAT_ID_BF_ADM=-123456789
CHAT_ID_BF_ADM_QUIZ=-123456789
LOJA_GROUP_ID=-123456789
LOJA_TOPIC_ID=123
BROADCAST_CHAT_ID=-123456789
BROADCAST_TOPIC_ID=456

# Notificações de YouTube (opcional)
YOUTUBE_CHANNEL_ID=UCxxxx
YOUTUBE_NOTIFY_CHAT_ID=-1001234567890  # usa BROADCAST_CHAT_ID se ausente
YOUTUBE_NOTIFY_TOPIC_ID=12345          # opcional
YOUTUBE_POLL_INTERVAL_SECONDS=300      # intervalo mínimo 60s

# Outros ajustes
BATTLE_COINS_REWARD=10
```

- `ADMINS` deve conter os IDs dos administradores do bot, separados por vírgula. Exemplo: `ADMINS=123456789,987654321`
- Para adicionar mais administradores, basta incluir mais IDs separados por vírgula.

Você pode obter a chave Gemini em https://aistudio.google.com/app/apikey
e o token do Telegram criando um bot em https://t.me/BotFather

### 3. Instale as dependências

```sh
pip install python-telegram-bot python-dotenv google-generativeai

pip install --upgrade -r requirements.txt
```

Se quiser atualizar o arquivo requirements.txt com as versões exatas dos pacotes instalados, execute o comando dentro do seu ambiente virtual (.venv):

```sh
# Ative o ambiente virtual antes, se necessário
# No Windows:
.venv\Scripts\activate
# No Linux/macOS:
source .venv/bin/activate

pip freeze > requirements.txt
```

### 4. Rode o bot principal

```sh
python main.py
```

### 5. Comandos disponíveis no Telegram

- `/addplayer <nome>` — Adiciona jogador
- `/dellplayer <nome>` — Remove jogador
- `/showranking` — Mostra ranking
- `/resetelo <nome>` — Reseta ELO de jogador
- `/reseteloall` — Reseta todos os jogadores
- `/ia <mensagem>` — Responde usando Gemini IA
- `/saldo <nome>` — Mostra saldo de moedas
- `/coinsranking` — Mostra ranking de moedas
- `/penalizar <Usuário> <quantidade>` — Remove moedas de um participante (admin)
- `/backup` — Gera um pacote ZIP com todo o conteúdo da pasta `storage/` e envia no privado do admin
- `/restore <arquivo|latest>` — Restaura o conteúdo de `storage/` a partir de um backup disponível
- (automático) Monitoramento do feed do YouTube configurado e publicação de cada novo vídeo

### 5.1 Notificações automáticas do YouTube

Para receber os vídeos mais recentes de um canal assim que forem publicados:

1. Configure no `.env` (ou `.env.example`) os campos:
   - `YOUTUBE_CHANNEL_ID` — ex.: `UCaGmdJSSiR7fkh2A-c6emsA` para o canal @g1globo.
   - `YOUTUBE_NOTIFY_CHAT_ID` — chat/grupo destino (usa `BROADCAST_CHAT_ID` se vazio).
   - `YOUTUBE_NOTIFY_TOPIC_ID` — opcional, tópico específico do chat.
   - `YOUTUBE_POLL_INTERVAL_SECONDS` — intervalo para verificar o feed (mínimo 60s; padrão 300s).
2. Reinicie o bot: o `register_youtube_notifier` agenda um job periódico no `job_queue` que busca o feed Atom do canal e posta cada vídeo novo no chat configurado, registrando o último vídeo em `storage/youtube_state.json` (@services/youtube_notifier.py#129-205).
3. Se quiser disparar manualmente, use `/youtube_last` (admin). O comando busca o vídeo mais recente e o envia imediatamente, útil quando se quer republicar em instantes ou testar a configuração (@main.py#419-443,610-620).

Erros comuns:
- Canal não configurado (`YOUTUBE_CHANNEL_ID` vazio) — o módulo ignora e loga aviso.
- Chat alvo não definido (`YOUTUBE_NOTIFY_CHAT_ID` e `BROADCAST_CHAT_ID` ausentes) — impede o anúncio.

### 6. Usando Docker

```sh
docker build -t battledex-arena-bot .
docker run --env-file .env battledex-arena-bot
```

Ou com docker-compose (persistindo a pasta `storage/`):

```sh
docker compose up -d --build
```

```sh
docker compose up
```

##### Rodando via WSL/Ubuntu
1. Abra o Ubuntu pelo Windows Terminal: `wsl -d Ubuntu` (se tiver outra distro, ajuste o nome). Para listar: `wsl -l -v`.
2. No shell do WSL:
   ```bash
   cd /mnt/d/Blockchain/battledex-arena-bot  # ou vá para a pasta atual do projeto
   docker compose up -d --build
   docker compose logs -f
   ```
3. Para parar: `docker compose down`.

##### Logs
- Todos os serviços: `docker compose logs -f --tail=200`
- Só o container principal: `docker logs -f --tail=200 battledex-arena-bot`

Pré-requisitos: Docker Desktop rodando no Windows (ou dockerd ativo no WSL) e arquivo `.env` na raiz do projeto.

#### Observações sobre Docker
- **O Docker NÃO usa venv**: as dependências são instaladas globalmente dentro do ambiente isolado do container.
- **Nada é enviado para a nuvem automaticamente**: a imagem criada fica salva apenas localmente no servidor, a não ser que você faça um `docker push` manual para o Docker Hub ou outro registro.
- **Arquivos e dependências**: tudo é copiado para `/app` dentro do container, e as dependências Python ficam disponíveis globalmente nesse ambiente.
- **Acessar arquivos do container**: para "entrar" no container e explorar os arquivos, rode:
  ```sh
  docker exec -it <nome_ou_id_do_container> bash
  # ou, se bash não estiver disponível:
  docker exec -it <nome_ou_id_do_container> sh
  ```
  O diretório do projeto será `/app`.

## Estrutura dos arquivos e pastas

- `main.py`: Bot principal do Telegram (ranking, loja, inventário, integração IA)
- `services/ia_bot.py`: Integração utilitária com Gemini (usada pelo comando `/ia`)
- `storage/`: **Todos os dados persistentes**
    - `rankingbf.db`: Ranking ELO
    - `coins.db`: Saldo/ranking de moedas
    - `inventario.db`, `shop.db`: Loja e inventário
    - `usuarios.json`: Cadastro de usuários
    - `scores.db`, `questions.db`, `questions.json`: Dados do quiz
    - `participation_bonus.json`: Histórico de bônus diário
    - `pokedex_cache.json`: Cache da Pokédex
- `loja/`: Módulos da loja e inventário de itens
    - `shop.py`, `comprar.py`, `inventario.py`, `cadastrar_itens.py`
    - `imagens/`: Assets de imagens da loja
- `financeiro/coins_db.py`: Funções de saldo, ranking e transferência de moedas
- `.env`: Variáveis de ambiente (tokens e chave Gemini)


---

---

Se precisar de mais comandos, integração com imagens ou outros ajustes, contribua ou abra uma issue!

## Observações
- Para cadastrar itens na loja, execute manualmente `loja/cadastrar_itens.py`.
- Certifique-se de configurar corretamente o arquivo `.env` antes de rodar o bot.
