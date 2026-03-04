# Repositório de Bancos e Persistência

Esta pasta agrupa todos os módulos responsáveis por persistência de dados SQLite do bot. A ideia é centralizar a lógica de acesso a banco em um único lugar, facilitando reutilização, organização e testes.

## Estrutura atual

| Arquivo | Responsabilidade |
| --- | --- |
| `ranking_db.py` | CRUD do ranking principal (ELO, vitórias/derrotas) e utilitário `calcular_pontos`. |
| `tournaments_db.py` | Cadastro de campeonatos, jogadores inscritos, registros de replays e ranking por campeonato. |
| `__init__.py` | Mantido vazio apenas para indicar que `repositories` é um pacote Python. |

## Convenções

1. **Isolamento do armazenamento**: sempre derive caminhos de `../storage` para manter os arquivos `.db` dentro da pasta de dados da raiz do projeto.
2. **APIs finas**: exponha apenas funções necessárias (ex.: `create_connection`, `create_table`, operações CRUD). Evite importar diretamente `sqlite3` em handlers.
3. **Commit explícito**: toda operação de escrita deve chamar `conn.commit()` antes de fechar a conexão.
4. **Mensagens de erro**: devolva mensagens em português para reutilização nos handlers de Telegram.

## Adicionando novos repositórios

1. Crie um novo arquivo `*_db.py` nesta pasta.
2. Siga o padrão abaixo:
   ```python
   import os
   import sqlite3

   STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage"))
   DB_PATH = os.path.join(STORAGE_DIR, "<nome>.db")

   def create_connection():
       os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
       return sqlite3.connect(DB_PATH)
   ```
3. Implemente funções utilitárias (ex.: `create_table`, `add_entry`, etc.).
4. Atualize os modules consumidores para importar via `from repositories.<arquivo> import ...`.
5. Opcional: documente brevemente o novo arquivo na tabela acima.

## Dicas

- Use `typing` para declarar tipos de retorno quando possível.
- Mantenha consultas SQL simples e parametrizadas para evitar SQL injection.
- Se um módulo crescer demais, considere dividir por contexto (ex.: `inventory_db.py`, `quiz_db.py`).

---
Atualize este README sempre que novos repositórios forem adicionados ou quando houver mudanças relevantes na convenção de acesso a dados.
