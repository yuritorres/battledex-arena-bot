# Handlers

Este diretório é o local para arquivos de handlers do bot.

## Como organizar
- Mova os handlers atuais para cá, por exemplo:
  - `handlers_ranking.py`
  - `handlers_ranking_message.py`
- Mantenha nomes claros e coesos por domínio (ex.: `ranking`, `loja`, `quiz`).

## O que cada handler faz
- `handlers_ranking.py`
  - `/addplayer <nome>`: adiciona jogador com Elo 1000 (admins).
  - `/dellplayer <nome>`: remove jogador (admins).
  - `/showranking`: mostra ranking formatado.
  - `/resetelo <nome>`: reseta Elo/estatísticas do jogador (admins).
  - `/reseteloall`: reseta Elo/estatísticas de todos (admins).
- `handlers_ranking_message.py`
  - `handle_message`: processa mensagens com `#ranking` (resultado de batalha) no formato:
    ```
    #ranking
    Jogador1 X x Y Jogador2
    link
    ```
    Faz: valida link de replay, evita duplicados, computa pontos, atualiza Elo, registra vencedor/perdedor e bonifica moedas do vencedor.

## Imports após mover
Se mover os arquivos para `handlers/`, ajuste os imports, por exemplo:
```python
from handlers.handlers_ranking import addplayer, dellplayer, showranking, resetelo, reseteloall
from handlers.handlers_ranking_message import handle_message
```

## Dicas
- Evite lógica de banco diretamente nos handlers; prefira serviços/repositórios.
- Reaproveite helpers comuns em módulos compartilhados para reduzir duplicação.
- Adicione testes para rotinas críticas (atualização de ranking, validação de resultados, etc.).
