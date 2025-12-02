# Desafio 3: Docker Compose Orquestrando Serviços

## Descrição do Projeto

Este projeto implementa uma arquitetura de microsserviços completa utilizando Docker Compose para orquestrar múltiplos serviços dependentes. A solução consiste em uma API REST para gerenciamento de tarefas (tasks) que utiliza PostgreSQL para persistência de dados e Redis para cache de consultas, demonstrando comunicação entre serviços, dependências e uso de variáveis de ambiente.

### Objetivo

Demonstrar orquestração de serviços Docker através de:
- API REST em Flask que gerencia tarefas (CRUD completo)
- Banco de dados PostgreSQL com volume persistente
- Cache Redis para otimização de performance
- Comunicação entre os três serviços via rede Docker customizada
- Uso de `depends_on` com health checks
- Variáveis de ambiente para configuração

## Arquitetura da Solução

### Componentes

**1. API Web (api-web)**
- Framework: Flask (Python 3.11)
- Porta: 5000
- Função: API REST para gerenciamento de tarefas
- Dependências: Aguarda banco-dados e cache-redis estarem saudáveis
- Endpoints: CRUD de tasks + health check + cache stats

**2. Banco de Dados (banco-dados)**
- Tecnologia: PostgreSQL 16
- Porta: 5432 (interna)
- Função: Armazenamento persistente de tarefas
- Volume: `dados_postgres` para persistência
- Inicialização: Script SQL automático com dados iniciais

**3. Cache (cache-redis)**
- Tecnologia: Redis 7
- Porta: 6379 (interna)
- Função: Cache de consultas para otimizar performance
- TTL: 60 segundos para dados em cache
- Estratégia: Cache invalidation em operações de escrita

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│           Rede: desafio3-network (bridge)                   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              api-web (Flask)                         │  │
│  │              Port: 5000                              │  │
│  │  Endpoints: /tasks, /health, /cache/stats           │  │
│  └────────────┬─────────────────────┬───────────────────┘  │
│               │                     │                       │
│               ▼                     ▼                       │
│  ┌─────────────────────┐  ┌────────────────────┐          │
│  │  banco-dados        │  │  cache-redis       │          │
│  │  (PostgreSQL 16)    │  │  (Redis 7)         │          │
│  │  Port: 5432         │  │  Port: 6379        │          │
│  │  Volume: persistente│  │  Memory cache      │          │
│  └─────────────────────┘  └────────────────────┘          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         │
         └──► Host: localhost:5000 (API acessível externamente)
```

### Fluxo de Comunicação

```
Cliente HTTP
    │
    ▼
GET /tasks ──► api-web ──► Verifica cache (cache-redis)
                  │            │
                  │            ├─► Cache HIT: Retorna dados
                  │            │
                  │            └─► Cache MISS:
                  ▼                    │
            Consulta banco-dados       │
                  │                    │
                  ▼                    │
            Retorna dados ─────────────┘
                  │
                  ▼
            Salva em cache (60s TTL)
                  │
                  ▼
            Retorna JSON ao cliente
```

## Decisões Técnicas

### 1. Ordem de Inicialização com Health Checks
Implementação de `depends_on` com `condition: service_healthy` garante que:
- PostgreSQL está aceitando conexões antes da API iniciar
- Redis está respondendo PING antes da API iniciar
- Evita erros de conexão durante startup
- Restart automático em caso de falha

### 2. Estratégia de Cache
Cache implementado com Redis usando padrão Cache-Aside:
- **Cache HIT**: Dados retornados do Redis (rápido)
- **Cache MISS**: Consulta PostgreSQL e popula cache
- **Cache Invalidation**: DELETE/UPDATE removem cache correspondente
- **TTL de 60s**: Balance entre performance e dados atualizados

### 3. Variáveis de Ambiente
Configurações externalizadas via environment variables:
- Credenciais do banco de dados
- Hosts e portas dos serviços
- Facilita mudança entre ambientes (dev/prod)
- Segurança: evita hardcoded credentials

### 4. Rede Interna
Serviços se comunicam via rede bridge customizada:
- DNS automático resolve nomes de containers
- PostgreSQL e Redis não expostos ao host (apenas internamente)
- API exposta na porta 5000 do host
- Isolamento e segurança

### 5. Persistência de Dados
Volume nomeado para PostgreSQL garante:
- Dados sobrevivem a `docker compose down`
- Facilita backup e restore
- Independente do ciclo de vida dos containers

## Estrutura de Arquivos

```
desafio3/
├── api/
│   ├── Dockerfile              # Imagem Python com Flask
│   ├── app.py                  # API REST com endpoints
│   ├── models.py               # Funções para acesso ao PostgreSQL
│   ├── cache.py                # Funções para acesso ao Redis
│   └── requirements.txt        # Dependências (flask, psycopg2, redis)
├── banco/
│   ├── Dockerfile              # Imagem PostgreSQL customizada
│   └── init.sql                # Schema e dados iniciais
├── docker-compose.yml          # Orquestração dos 3 serviços
└── README.md                   # Este arquivo
```

## Tecnologias Utilizadas

- **Docker**: 20.10+ (containerização)
- **Docker Compose**: 2.0+ (orquestração)
- **Python**: 3.11 (linguagem da API)
- **Flask**: 3.0.0 (framework web)
- **PostgreSQL**: 16 (banco de dados relacional)
- **Redis**: 7 (cache em memória)
- **psycopg2**: 2.9.9 (driver PostgreSQL)
- **redis-py**: 5.0.1 (cliente Redis)
- **Alpine Linux**: 3.x (sistema operacional base)

## Pré-requisitos

Antes de executar o projeto, certifique-se de ter instalado:

- Docker Engine 20.10 ou superior
- Docker Compose 2.0 ou superior

### Verificar instalação:

```bash
docker --version
docker compose version
```

## Instruções de Execução

### Passo 1: Iniciar todos os serviços

```bash
cd desafio3
docker compose up --build -d
```

**Ordem de inicialização automática:**
1. `banco-dados` inicia primeiro
2. `cache-redis` inicia em paralelo
3. Aguarda health checks ficarem "healthy"
4. `api-web` inicia por último

### Passo 2: Verificar status dos serviços

```bash
docker compose ps
```

**Saída esperada:**
```
NAME          IMAGE                  STATUS                    PORTS
api-web       desafio3-api-web       Up (healthy)              0.0.0.0:5000->5000/tcp
banco-dados   desafio3-banco-dados   Up (healthy)              5432/tcp
cache-redis   redis:7-alpine         Up (healthy)              6379/tcp
```

### Passo 3: Visualizar logs dos serviços

**Logs de todos os serviços:**
```bash
docker compose logs -f
```

**Logs apenas da API:**
```bash
docker logs -f api-web
```

**Últimas 50 linhas:**
```bash
docker compose logs --tail=50
```

### Passo 4: Testar health check da API

```bash
curl http://localhost:5000/health
```

**Resposta esperada:**
```json
{
  "api": "healthy",
  "cache": "healthy",
  "database": "healthy"
}
```

### Passo 5: Testar endpoints da API

#### Listar todas as tarefas (primeira vez - database)

```bash
curl http://localhost:5000/tasks
```

**Resposta:**
```json
{
  "source": "database",
  "count": 3,
  "tasks": [
    {
      "id": 1,
      "title": "Setup Docker Environment",
      "description": "Configure all containers and networks",
      "status": "completed",
      "created_at": "2025-12-02T10:00:00",
      "updated_at": "2025-12-02T10:00:00"
    },
    ...
  ]
}
```

#### Listar tarefas novamente (segunda vez - cache)

```bash
curl http://localhost:5000/tasks
```

**Resposta:**
```json
{
  "source": "cache",
  "count": 3,
  "tasks": [...]
}
```

**Observe:** `"source": "cache"` indica que dados vieram do Redis!

#### Buscar tarefa específica

```bash
curl http://localhost:5000/tasks/1
```

#### Criar nova tarefa

```bash
curl -X POST http://localhost:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Escrever README",
    "description": "Documentar o projeto completo",
    "status": "in_progress"
  }'
```

**Resposta:**
```json
{
  "message": "Task created successfully",
  "task": {
    "id": 4,
    "title": "Escrever README",
    "description": "Documentar o projeto completo",
    "status": "in_progress",
    "created_at": "2025-12-02T11:00:00",
    "updated_at": "2025-12-02T11:00:00"
  }
}
```

#### Atualizar tarefa

```bash
curl -X PUT http://localhost:5000/tasks/4 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

#### Deletar tarefa

```bash
curl -X DELETE http://localhost:5000/tasks/4
```

### Passo 6: Verificar estatísticas do cache

```bash
curl http://localhost:5000/cache/stats
```

**Resposta:**
```json
{
  "connected_clients": 1,
  "used_memory_human": "1.2M",
  "total_commands_processed": 42,
  "keyspace_hits": 15,
  "keyspace_misses": 5
}
```

### Passo 7: Limpar cache manualmente

```bash
curl -X POST http://localhost:5000/cache/clear
```

### Passo 8: Acessar serviços diretamente

**Acessar PostgreSQL:**
```bash
docker exec -it banco-dados psql -U admin -d tasks_db
```

```sql
SELECT * FROM tasks;
\q
```

**Acessar Redis:**
```bash
docker exec -it cache-redis redis-cli
```

```
KEYS *
GET all_tasks
EXIT
```

### Passo 9: Verificar rede Docker

```bash
docker network inspect desafio3-network
```

### Passo 10: Parar e remover serviços

**Parar containers (mantém volumes):**
```bash
docker compose down
```

**Remover tudo incluindo volumes:**
```bash
docker compose down -v
```

## Funcionamento Detalhado

### Fluxo de uma Requisição GET /tasks

1. **Cliente faz requisição HTTP GET** para `http://localhost:5000/tasks`
2. **API recebe requisição** e loga no console
3. **Verifica cache Redis** usando chave `all_tasks`
4. **Se Cache HIT:**
   - Retorna dados do Redis imediatamente
   - Log: "Cache HIT - Retornando dados do Redis"
   - Response: `"source": "cache"`
5. **Se Cache MISS:**
   - Log: "Cache MISS - Consultando banco de dados"
   - Conecta ao PostgreSQL via `banco-dados:5432`
   - Executa query: `SELECT * FROM tasks ORDER BY created_at DESC`
   - Serializa datetime para ISO format
   - Salva resultado no Redis com TTL de 60s
   - Response: `"source": "database"`
6. **Retorna JSON** ao cliente

### Fluxo de uma Requisição POST /tasks

1. **Cliente envia dados JSON** via POST
2. **API valida** presença do campo `title`
3. **Insere no PostgreSQL** usando prepared statement
4. **Invalida cache** removendo chave `all_tasks`
5. **Retorna task criada** com ID gerado

### Health Checks

**PostgreSQL:**
```bash
pg_isready -U admin -d tasks_db
```
Verifica se banco está aceitando conexões.

**Redis:**
```bash
redis-cli ping
```
Verifica se Redis responde PONG.

**API:**
```bash
wget --spider http://localhost:5000/health
```
Verifica se API está respondendo HTTP 200.

## Demonstração de Cache

Execute esta sequência para ver o cache em ação:

```bash
time curl http://localhost:5000/tasks
time curl http://localhost:5000/tasks
time curl http://localhost:5000/tasks
```

**Primeira requisição:** ~100-200ms (consulta PostgreSQL)
**Segunda e terceira:** ~10-20ms (retorna do Redis)

Veja os logs:
```bash
docker logs api-web --tail=20
```

Você verá:
```
Cache MISS - Consultando banco de dados
Cache SET - Key: all_tasks - Expiration: 60s
...
Cache HIT - Retornando dados do Redis
Cache GET - Key: all_tasks - FOUND
...
Cache HIT - Retornando dados do Redis
Cache GET - Key: all_tasks - FOUND
```

## Endpoints da API

### GET /
Retorna informações sobre a API e lista de endpoints disponíveis.

### GET /health
Health check que verifica status de API, database e cache.

### GET /tasks
Lista todas as tarefas (usa cache).

### GET /tasks/:id
Retorna tarefa específica por ID (usa cache).

### POST /tasks
Cria nova tarefa. Body JSON:
```json
{
  "title": "string (obrigatório)",
  "description": "string (opcional)",
  "status": "pending|in_progress|completed (opcional)"
}
```

### PUT /tasks/:id
Atualiza tarefa existente. Body JSON com campos a atualizar.

### DELETE /tasks/:id
Remove tarefa por ID.

### GET /cache/stats
Retorna estatísticas do Redis (hits, misses, memória).

### POST /cache/clear
Limpa todo o cache do Redis.

## Variáveis de Ambiente

### API (api-web)

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| DB_HOST | banco-dados | Hostname do PostgreSQL |
| DB_NAME | tasks_db | Nome do banco de dados |
| DB_USER | admin | Usuário do PostgreSQL |
| DB_PASSWORD | admin123 | Senha do PostgreSQL |
| DB_PORT | 5432 | Porta do PostgreSQL |
| REDIS_HOST | cache-redis | Hostname do Redis |
| REDIS_PORT | 6379 | Porta do Redis |

### PostgreSQL (banco-dados)

| Variável | Valor | Descrição |
|----------|-------|-----------|
| POSTGRES_DB | tasks_db | Nome do banco criado |
| POSTGRES_USER | admin | Usuário administrador |
| POSTGRES_PASSWORD | admin123 | Senha do admin |

## Volumes

### dados_postgres
- **Tipo:** Named Volume
- **Montado em:** `/var/lib/postgresql/data`
- **Função:** Persiste dados do PostgreSQL
- **Ciclo de vida:** Independente dos containers

## Troubleshooting

### API não inicia (unhealthy)

Verifique logs:
```bash
docker logs api-web
```

Verifique se dependências estão healthy:
```bash
docker compose ps
```

### Erro de conexão com PostgreSQL

```bash
docker exec -it api-web ping banco-dados
docker exec -it banco-dados pg_isready -U admin
```

### Cache não funciona

Verifique Redis:
```bash
docker exec -it cache-redis redis-cli ping
docker logs cache-redis
```

Limpe e teste novamente:
```bash
curl -X POST http://localhost:5000/cache/clear
curl http://localhost:5000/tasks
curl http://localhost:5000/tasks
```

### Porta 5000 já em uso

Altere no `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"
```

### Reconstruir completamente

```bash
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

## Conceitos Importantes

### Docker Compose
Ferramenta para definir e executar aplicações Docker multi-container usando arquivo YAML.

### Service Dependencies
`depends_on` com health checks garante ordem correta de inicialização.

### Named Volumes
Volumes gerenciados pelo Docker que persistem dados independentemente dos containers.

### Health Checks
Verificações periódicas do estado dos containers para garantir disponibilidade.

### Cache-Aside Pattern
Estratégia onde aplicação verifica cache primeiro, consulta banco em caso de miss, e popula cache.