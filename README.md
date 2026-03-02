# BattleDex Arena — Bot Telegram (Ranking + Gemini IA)

Este projeto contém um bot para Telegram voltado para a comunidade de batalhas estilo Pokémon Showdown. Ele gerencia ranking de jogadores (ELO, vitórias, derrotas) e integra respostas por IA (Gemini/Google Generative AI) via comando `/ia`.

## Funcionalidades
- Ranking de jogadores (adicionar, remover, mostrar ranking, resetar ELO)
- Comando `/ia <mensagem>`: responde usando a IA Gemini
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

Crie um arquivo `.env` na pasta `battledex-arena-bot` com:
```
GEMINI_API_KEY=SuaChaveGeminiAqui
TELEGRAM_TOKEN=SeuTokenTelegramAqui
ADMINS=123456789,987654321
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

### 6. Usando Docker

```sh
docker build -t battledex-arena-bot .
docker run --env-file .env battledex-arena-bot
```

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
- `ia_bot.py`: Integração utilitária com Gemini (usada pelo comando `/ia`)
- `financeiro/`: Módulo de moedas e banco de dados de saldo
    - `coins_db.py`: Funções de saldo, ranking e transferência de moedas
    - `coins.db`: Banco de dados SQLite de moedas
- `loja/`: Módulos da loja e inventário de itens
    - `shop.py`: Lista e busca itens da loja
    - `comprar.py`: Lógica de compra de itens
    - `inventario.py`: Gerenciamento de inventário dos usuários
    - `cadastrar_itens.py`: Script utilitário para cadastrar itens (executado manualmente)
- `.env`: Variáveis de ambiente (tokens e chave Gemini)
- `usuarios.json`: Cadastro de usuários
- `coins.db`, `rankingbf.db`: Bancos de dados SQLite


---

---

Se precisar de mais comandos, integração com imagens ou outros ajustes, contribua ou abra uma issue!

## Observações
- Para cadastrar itens na loja, execute manualmente `loja/cadastrar_itens.py`.
- Certifique-se de configurar corretamente o arquivo `.env` antes de rodar o bot.
