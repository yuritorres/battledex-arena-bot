# 🗺️ BattleDex Arena Bot - Roadmap de Desenvolvimento

## 📋 **Visão Geral**
BattleDex Arena Bot é um bot Telegram para gerenciamento de torneios Pokémon, ranking ELO, sistema de moedas e quiz integrado.

---

## 🚨 **Issues Críticas (Prioridade Alta)**

### ✅ **Consertado**
- [x] Código duplicado da classe `BrasiliaFormatter`
- [x] Persistência de dados no Docker

### 🔥 **Urgente**
- [ ] **Bug de Pontuação de Participação**: Usuário ganha pontos múltiplas vezes ao reiniciar o bot no mesmo dia
- [ ] **Refatoração do main.py**: 531 linhas - precisa ser dividido em módulos
- [ ] **Imports duplicados**: `import os` aparece múltiplas vezes

---

## 🏗️ **Arquitetura & Estrutura**

### **Estado Atual**
```
battledex-arena-bot/
├── main.py (531 linhas) ❌ Muito grande
├── handlers/ ✅ Bem organizado
├── repositories/ ✅ Bom padrão
├── services/ ✅ Separação correta
├── utils/ ✅ Módulo logger criado
└── storage/ ✅ Persistência OK
```

### **Melhorias Necessárias**
- [ ] **Dividir main.py** em:
  - `bot/app.py` - Configuração principal
  - `bot/handlers.py` - Registro de handlers
  - `bot/config.py` - Variáveis de ambiente
- [ ] **Criar `config/`** para configurações centralizadas
- [ ] **Implementar injeção de dependências**

---

## 🔧 **Refatoração de Código**

### **main.py - Divisão Sugerida**
```python
# bot/app.py
class BattleDexBot:
    def __init__(self):
        self.app = ApplicationBuilder().token(token).build()
        self.register_handlers()
    
    def register_handlers(self):
        # Mover todos os app.add_handler()

# bot/handlers.py  
def register_command_handlers(app):
    # Mover registro de comandos

def register_message_handlers(app):
    # Mover registro de mensagens
```

### **Imports e Organização**
- [ ] **Remover imports duplicados**
- [ ] **Agrupar imports por tipo** (stdlib, third-party, local)
- [ ] **Criar `__init__.py`** em todos os módulos

---

## 🐛 **Bugs Conhecidos**

### **1. Pontuação de Participação**
**Problema**: Reiniciar o bot múltiplas vezes no mesmo dia concede pontos repetidos
**Localização**: `bonus/participation_bonus.py`
**Solução**: Implementar controle por data + usuário

### **2. Validação de Entrada**
**Problema**: Falta validação em comandos críticos
**Impacto**: Possível corrupção de dados
**Solução**: Adicionar decorators de validação

### **3. Tratamento de Erros**
**Problema**: Exceções genéricas sem logging específico
**Solução**: Implementar error handling granular

---

## 📊 **Banco de Dados & Persistência**

### **Estado Atual** ✅
- Volume Docker configurado
- 10 bancos SQLite funcionando
- Dados persistindo corretamente

### **Melhorias**
- [ ] **Migration system** para alterações de schema
- [ ] **Backup automático** dos bancos
- [ ] **Índices** para performance
- [ ] **Conexão pool** para concorrência

---

## 🔐 **Segurança**

### **Issues Identificadas**
- [x] **Hardcoded admin ID**: no comando usado
- [ ] **SQL Injection potencial**: Queries sem parâmetros
- [ ] **Env vars expostas**: `.env` no Git (verificar `.gitignore`)

### **Melhorias**
- [ ] **Admin system dinâmico** via banco ou config
- [ ] **Input sanitization** em todos os comandos
- [ ] **Rate limiting** para comandos
- [ ] **Audit log** para ações administrativas

---

## 🚀 **Novas Funcionalidades**

### **Short Term (1-2 semanas)**
- [ ] **Dashboard Admin** web para gerenciamento
- [ ] **Export/Import** de dados do ranking
- [ ] **Sistema de notificações** para eventos
- [x] **Comando de backup/restore** — comando envia o ZIP apenas no privado do admin
- [ ] **Comandos inline de consulta rápida** (ex.: digitar @BattleDexBot em qualquer chat para mostrar ranking ou saldo)
- [ ] **Links com parâmetros (`start`/`startgroup`)** para inscrição em torneios e onboarding guiado direto do BotFather
- [ ] **Atalhos no menu de anexos** para reportar resultados sem sair do grupo (quando o Telegram liberar para o bot)
- [ ] **Comandos inline de consulta rápida** (ex.: digitar @BattleDexBot em qualquer chat para mostrar ranking ou saldo)
- [ ] **Links com parâmetros (`start`/`startgroup`)** para inscrição em torneios e onboarding guiado direto do BotFather
- [ ] **Webhook com Pokémon Showdown** para registrar automaticamente resultados de salas/grupos selecionados
- [ ] **Importação de replays Showdown** (colou o link → bot puxa metadados e atualiza ranking interno)
- [ ] **Modo treino PvE alinhado às partidas Showdown** — IA simples com movesets oficiais e regras usadas no replay [Gen4 Ubers](https://replay.pokemonshowdown.com/gen4ubers-2373374930) para permitir treinos fora dos torneios BattleDex
- [ ] **Logs de batalha no formato Showdown** enviados no privado após cada partida, incluindo weather/status/movimentos como no replay, para revisões rápidas e consistentes com o fluxo da plataforma
- [ ] **Sistema de notificações push via Telegram** para alertas de torneios e atualizações de ranking
- [ ] **Auto-moderation inteligente** para grupos de torneio, detectando spam e violações de regras
- [ ] **Análise automática de replays** para identificar erros comuns e sugerir melhorias pós-partida

#### ✨ Ideias trazidas do [showdown-battlebot](https://github.com/Agetian/showdown-battlebot)
- [ ] **Plug-in de bots de batalha**: expor uma interface BattleBot com `find_best_move`, permitindo selecionar estratégias via `BATTLE_BOT` (ex.: `safest`, `most_damage`). Cada bot passa a ser um módulo independente escolhido por variável de ambiente, o que habilita alternar lógica de decisão sem alterar o core do BattleDex.
- [ ] **Expectiminimax "Safest" para IA**: reaproveitar a busca de dois turnos com média ponderada de resultados para nosso modo treino PvE. A árvore combina todas as transições possíveis e calcula o movimento com menor perda esperada, reproduzindo o comportamento determinístico usado no projeto referência.
- [ ] **Suporte a datasets de times**: aceitar arquivos JSON em `storage/team_datasets/` para melhorar a leitura de sets adversários e alimentar o modo treino. Na prática, carregamos composições/itens conhecidos antes das batalhas e usamos essas informações durante o cálculo de melhores respostas.
- [ ] **Integração Nash Equilibrium (Docker)**: investigar uso do Gambit para cálculos probabilísticos quando estivermos executando via Docker. O bot monta a matriz de payoff com as opções conhecidas, usa o solver do Gambit e sorteia uma jogada seguindo a distribuição ótima encontrada.
- [ ] **Configuração avançada por env file**: mapear variáveis como `WEBSOCKET_URI`, `BOT_MODE`, `POKEMON_MODE`, `SAVE_REPLAY` para facilitar conexões diretas com Showdown. Assim replicamos o fluxo do showdown-battlebot, mantendo um `.env` rico para definir credenciais, modo de desafio, time escolhido e logging.

### **Medium Term (1-2 meses)**
- [ ] **API REST** para integração externa
- [ ] **Sistema de badges/conquistas**
- [ ] **Torneios automatizados** (swiss, round-robin)
- [ ] **Integração com Discord**
- [ ] **Mini App Telegram** para painel do admin/jogador sem sair do app
- [ ] **Web Login** para conectar contas BattleDex a serviços externos usando a conta Telegram
- [ ] **Sincronização de torneios Showdown** (criar/iniciar Auto-DQ diretamente do bot, inspirado nas ferramentas nativas da plataforma)
- [ ] **Leaderboard unificada** Showdown ↔️ BattleDex (importa ladder/elo externo e aplica bonificações locais)
- [ ] **PvP assíncrono entre jogadores** (desafios pairados por elo, registrando replays no formato BattleDex/Showdown para consulta)
- [ ] **Suporte a múltiplos Pokémon por partida** (times 3v3/6v6 como no replay, com alternância em turnos e persistência de status)
- [ ] **Sistema de itens e habilidades em batalhas** (berries, choice items, habilidades passivas que afetam dano e status, seguindo o modelo do link)
- [ ] **Batalhas simultâneas com isolamento de estado** para permitir múltiplas partidas Showdown-like sem bloquear o bot
- [ ] **Modo espectador para torneios ao vivo** para acompanhar partidas em tempo real
- [ ] **Matchmaking baseado em taxa de vitória** para equilibrar PvP
- [ ] **Eventos sazonais com recompensas especiais** (temas, itens exclusivos)

### **Long Term (3+ meses)**
- [ ] **Machine Learning** para balanceamento de times
- [ ] **Mobile app** companion
- [ ] **Multi-linguagem** suporte
- [ ] **Cloud deployment** (AWS/GCP)
- [ ] **Jogos HTML5 integrados** (mini desafios PVE/PVP que dão moedas)
- [ ] **Sticker packs e custom emoji temáticos** liberados como recompensas de temporada
- [ ] **Promoção no Mini App Store / atalhos na home** para ampliar alcance e reengajamento
- [ ] **Jogos HTML5 integrados** (mini desafios PVE/PVP que dão moedas)
- [ ] **Sticker packs e custom emoji temáticos** liberados como recompensas de temporada
- [ ] **Battle bot avançado estilo Showdown** (IA básica para sparring/treino e eventos "bot battle royale")
- [ ] **Sistema de efeitos secundários e condições climáticas** (status, buffs/debuffs, weather control) reproduzindo o comportamento observado no replay
- [ ] **Análises pós-jogo com recomendações de jogadas** usando os replays BattleDex/Showdown para sugerir linhas alternativas em partidas reais
- [ ] **Hub social in-bot orientado a partidas** para matchmaking rápido, organização de clãs e temporadas baseadas em histórico de confrontos
- [ ] **Integração com foruns externos** para discussões de estratégias
- [ ] **Sistema de conquistas avançadas** com badges visuais
- [ ] **Análise preditiva de partidas** usando dados históricos para dicas

---

## 📈 **Performance & Monitoramento**

### **Métricas Necessárias**
- [ ] **Response time** dos comandos
- [ ] **Memory usage** do bot
- [ ] **Database query performance**
- [ ] **User engagement** metrics

### **Implementação**
- [ ] **Prometheus + Grafana** stack
- [ ] **Health checks** automáticos
- [ ] **Alert system** para erros
- [ ] **Performance profiling**

---

## 🧪 **Testes & Qualidade**

### **Cobertura de Testes**
- [ ] **Unit tests** para handlers (0% atual)
- [ ] **Integration tests** para bancos
- [ ] **E2E tests** para fluxos críticos
- [ ] **Load tests** para performance

### **Qualidade de Código**
- [ ] **Black** para formatação
- [ ] **Flake8** para linting
- [ ] **mypy** para type hints
- [ ] **Pre-commit hooks**

---

## 📚 **Documentação**

### **Technical Docs**
- [x] **README.md** existe
- [ ] **API Documentation**
- [ ] **Database Schema**
- [ ] **Deployment Guide**

### **User Docs**
- [ ] **User Manual** completo
- [ ] **Admin Guide**
- [ ] **FAQ** com problemas comuns
- [ ] **Video tutorials**

---

## 🔄 **CI/CD & Deploy**

### **Pipeline Atual**
- [x] **Docker** configurado
- [x] **Docker Compose** funcionando

### **Melhorias**
- [ ] **GitHub Actions** para CI/CD
- [ ] **Automated testing** pipeline
- [ ] **Multi-environment** deploy (dev/staging/prod)
- [ ] **Rollback strategy**

---

## 📊 **Timeline Sugerida**

### **Sprint 1 (2 semanas) - Críticos**
- Consertar bug de pontuação de participação
- Refatorar main.py em módulos
- Implementar validação de entrada
- Adicionar tratamento de erros

### **Sprint 2 (2 semanas) - Qualidade**
- Implementar testes unitários
- Setup CI/CD pipeline
- Melhorar segurança (admin system)
- Documentação técnica

### **Sprint 3 (2 semanas) - Features**
- Dashboard admin web
- Sistema de backup/restore
- Export/Import de dados
- Monitoramento básico

### **Sprint 4+ (contínuo) - Evolução**
- Novas funcionalidades
- Performance improvements
- Mobile app companion
- Cloud deployment

---

## 🎯 **KPIs & Success Metrics**

### **Technical KPIs**
- **Code coverage**: >80%
- **Response time**: <500ms
- **Uptime**: >99.9%
- **Bug density**: <1 bug/1000 LOC

### **Business KPIs**
- **Active users**: +20% mês
- **Tournament participation**: +15% mês  
- **User retention**: >80%
- **Command success rate**: >95%

---

## 🚦 **Status Dashboard**

| Categoria | Status | Prioridade | Progresso |
|-----------|--------|------------|------------|
| Bugs Críticos | 🔥 Urgente | Alta | 20% |
| Refatoração | 🟡 Em andamento | Alta | 40% |
| Segurança | 🟡 Planejado | Média | 0% |
| Testes | 🔴 Não iniciado | Média | 0% |
| Documentação | 🟡 Parcial | Baixa | 30% |
| Novas Features | 🟡 Planejado | Baixa | 0% |

---

**Última atualização**: Março 2026
**Maintainer**: BattleDex Team
**Version**: 1.0.0-roadmap
