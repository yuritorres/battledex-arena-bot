# Sincronização de Storage - Docker Windows

## Problema
Arquivos criados dentro do container Docker (como `replay_stats.json`) não aparecem imediatamente no diretório local Windows devido a limitações de sincronização do Docker Desktop.

## Soluções Criadas

### 1. docker-compose.local.yml
- Volume duplicado para forçar sincronização
- Configuração de usuário para compatibilidade

### 2. docker-compose.dev.yml  
- Configuração otimizada para Windows
- `consistency: cached` para melhor performance
- User mapping para permissões corretas

### 3. docker-compose.sync.yml
- Backup automático para `./local_storage`
- Script de sincronização no entrypoint
- Cópia dos arquivos para diretório local

## Como Usar

### Para desenvolvimento local:
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

### Para sincronização automática:
```bash
docker-compose -f docker-compose.sync.yml up -d --build
```

### Para manter configuração atual:
```bash
docker-compose up -d --build
```

## Verificação

Depois de usar `/replay` no bot, verifique se os arquivos aparecem:

```bash
ls -la ./storage/
ls -la ./local_storage/  # se usar sync.yml
```

## Arquivos Importantes

- `replay_stats.json` - Estatísticas de replays
- `usuarios.json` - Usuários registrados  
- `*.db` - Bancos de dados SQLite

## Troubleshooting

Se os arquivos ainda não sincronizarem:
1. Reinicie o container: `docker-compose restart`
2. Use o sync.yml para backup automático
3. Verifique permissões do diretório local
