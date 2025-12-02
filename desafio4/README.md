# Desafio 4: Microsserviços Independentes

## Descrição do Projeto

Este projeto implementa dois microsserviços independentes que se comunicam via HTTP/REST. O primeiro microsserviço fornece dados de usuários, enquanto o segundo consome esses dados e adiciona informações agregadas e calculadas, demonstrando comunicação inter-serviços em uma arquitetura de microsserviços.

### Objetivo

Demonstrar comunicação entre microsserviços independentes através de:
- Microsserviço A (Users Service): Retorna lista de usuários em formato JSON
- Microsserviço B (Aggregator Service): Consome o serviço A e adiciona informações calculadas
- Comunicação via requisições HTTP REST
- Isolamento de serviços com Dockerfiles separados
- Descoberta de serviços via DNS do Docker

## Arquitetura da Solução

### Componentes

**1. Serviço de Usuários (servico-usuarios)**
- Framework: Flask (Python 3.11)
- Porta: 5001
- Função: API REST que fornece dados de usuários
- Dados: Lista de usuários com id, nome, email, role e data de criação
- Endpoints: `/users`, `/users/<id>`, `/health`

**2. Serviço Agregador (servico-agregador)**
- Framework: Flask (Python 3.11)
- Porta: 5002
- Função: Consome dados do serviço de usuários e adiciona informações calculadas
- Processamento: Calcula dias ativos, status do usuário, gera estatísticas
- Endpoints: `/users/summary`, `/users/<id>/summary`, `/stats`, `/health`

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│         Rede: desafio4-network (bridge)                 │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         servico-agregador (Aggregator)           │  │
│  │              Port: 5002                          │  │
│  │  - GET /users/summary                            │  │
│  │  - GET /users/<id>/summary                       │  │
│  │  - GET /stats                                    │  │
│  └────────────────┬─────────────────────────────────┘  │
│                   │                                     │
│                   │ HTTP Request                        │
│                   │ GET http://servico-usuarios:5001    │
│                   ▼                                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │         servico-usuarios (Users)                 │  │
│  │              Port: 5001                          │  │
│  │  - GET /users                                    │  │
│  │  - GET /users/<id>                               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
         │                          │
         └──► Host: 5001            └──► Host: 5002
         (Acesso externo)           (Acesso externo)
```

### Fluxo de Comunicação

```
Cliente HTTP
    │
    ▼
GET /users/summary (5002)
    │
    ▼
servico-agregador
    │
    ├─► HTTP GET http://servico-usuarios:5001/users
    │                      │
    │                      ▼
    │              servico-usuarios
    │                      │
    │                      ▼
    │              Retorna JSON com usuários
    │                      │
    ◄──────────────────────┘
    │
    ▼
Processa dados:
  - Calcula dias ativos
  - Define status (Novo/Intermediário/Experiente/Veterano)
  - Gera resumo textual
    │
    ▼
Retorna JSON enriquecido
```

## Decisões Técnicas

### 1. Comunicação HTTP REST
Escolha do protocolo HTTP REST para comunicação porque:
- Padrão amplamente adotado em microsserviços
- Stateless e baseado em texto (JSON)
- Fácil de debugar e testar
- Compatível com qualquer linguagem/framework

### 2. Service Discovery via DNS
Uso de DNS interno do Docker para descoberta de serviços:
- Nome do container resolve para seu IP automaticamente
- `servico-usuarios` é acessível via `http://servico-usuarios:5001`
- Sem necessidade de configuração manual de IPs
- Facilita escalabilidade e manutenção

### 3. Dockerfiles Separados
Cada serviço possui seu próprio Dockerfile:
- Isolamento completo de dependências
- Possibilidade de usar diferentes tecnologias
- Deploy independente
- Facilita escalabilidade horizontal

### 4. Health Checks
Implementação de health checks em ambos serviços:
- Verifica disponibilidade do serviço
- Permite restart automático em caso de falha
- Integração com orquestradores (Kubernetes, Docker Swarm)

### 5. Retry Logic e Tratamento de Erros
Agregador implementa tratamento robusto de erros:
- Timeout de 5 segundos para requisições
- Tratamento de ConnectionError
- Tratamento de Timeout
- Códigos HTTP apropriados (503 Service Unavailable, 502 Bad Gateway)

## Estrutura de Arquivos

```
desafio4/
├── servico-usuarios/
│   ├── Dockerfile              # Imagem Python com Flask
│   ├── app.py                  # API REST de usuários
│   └── requirements.txt        # Dependências (flask, werkzeug)
├── servico-agregador/
│   ├── Dockerfile              # Imagem Python com Flask + requests
│   ├── app.py                  # API REST agregadora
│   └── requirements.txt        # Dependências (flask, requests, werkzeug)
├── docker-compose.yml          # Orquestração dos 2 serviços
└── README.md                   # Este arquivo
```

## Tecnologias Utilizadas

- **Docker**: 20.10+ (containerização)
- **Docker Compose**: 2.0+ (orquestração)
- **Python**: 3.11 (linguagem de programação)
- **Flask**: 3.0.0 (framework web)
- **Requests**: 2.31.0 (cliente HTTP para Python)
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

### Passo 1: Iniciar os microsserviços

```bash
cd desafio4
docker compose up --build -d
```

**Ordem de inicialização:**
1. `servico-usuarios` inicia primeiro
2. Health check verifica se está healthy
3. `servico-agregador` inicia após usuários estar saudável

### Passo 2: Verificar status dos serviços

```bash
docker compose ps
```

**Saída esperada:**
```
NAME                 IMAGE                       STATUS
servico-usuarios     desafio4-servico-usuarios   Up (healthy)
servico-agregador    desafio4-servico-agregador  Up (healthy)
```

### Passo 3: Testar Serviço de Usuários (Microsserviço A)

#### Listar todos os usuários

```bash
curl http://localhost:5001/users
```

**Resposta:**
```json
{
  "count": 5,
  "service": "users-service",
  "users": [
    {
      "created_at": "2024-12-02T11:00:00.000000",
      "email": "joao.silva@email.com",
      "id": 1,
      "name": "João Silva",
      "role": "Developer"
    },
    ...
  ]
}
```

#### Buscar usuário específico

```bash
curl http://localhost:5001/users/1
```

#### Verificar health

```bash
curl http://localhost:5001/health
```

### Passo 4: Testar Serviço Agregador (Microsserviço B)

#### Obter resumo de todos os usuários

```bash
curl http://localhost:5002/users/summary
```

**Resposta:**
```json
{
  "service": "aggregator-service",
  "source": "users-service",
  "count": 5,
  "users": [
    {
      "id": 1,
      "name": "João Silva",
      "email": "joao.silva@email.com",
      "role": "Developer",
      "created_at": "2024-12-02T11:00:00.000000",
      "days_active": 365,
      "status": "Veterano",
      "summary": "João Silva (Developer) - Veterano - 365 dias na plataforma"
    },
    ...
  ]
}
```

**Observe:** O agregador adicionou `days_active`, `status` e `summary`!

#### Obter resumo de usuário específico

```bash
curl http://localhost:5002/users/1/summary
```

**Resposta:**
```json
{
  "service": "aggregator-service",
  "source": "users-service",
  "user": {
    "id": 1,
    "name": "João Silva",
    "email": "joao.silva@email.com",
    "role": "Developer",
    "created_at": "2024-12-02T11:00:00.000000",
    "days_active": 365,
    "status": "Veterano",
    "years_active": 1.0,
    "months_active": 12.2,
    "summary": "João Silva (Developer) - Veterano - 365 dias na plataforma"
  }
}
```

#### Obter estatísticas agregadas

```bash
curl http://localhost:5002/stats
```

**Resposta:**
```json
{
  "service": "aggregator-service",
  "total_users": 5,
  "users_by_status": {
    "Veterano": 2,
    "Experiente": 1,
    "Intermediario": 1,
    "Novo": 1
  },
  "users_by_role": {
    "Developer": 2,
    "Designer": 1,
    "Manager": 1,
    "QA Engineer": 1
  },
  "timestamp": "2025-12-02T11:45:00.000000"
}
```

### Passo 5: Visualizar logs

**Logs do serviço de usuários:**
```bash
docker logs -f servico-usuarios
```

**Logs do agregador:**
```bash
docker logs -f servico-agregador
```

**Ambos simultaneamente:**
```bash
docker compose logs -f
```

### Passo 6: Verificar comunicação nos logs

Execute uma requisição e veja os logs:

```bash
curl http://localhost:5002/users/summary
docker compose logs --tail=20
```

**Você verá:**
```
servico-agregador | Chamando servico de usuarios: http://servico-usuarios:5001/users
servico-usuarios  | Requisicao recebida: GET /users
servico-agregador | Processados 5 usuarios com informacoes agregadas
```

### Passo 7: Testar isolamento de serviços

Cada serviço pode ser acessado independentemente:

```bash
curl http://localhost:5001/users
curl http://localhost:5002/users/summary
```

Parar apenas o agregador:
```bash
docker stop servico-agregador
curl http://localhost:5001/users
```

Serviço de usuários continua funcionando!

### Passo 8: Inspecionar rede Docker

```bash
docker network inspect desafio4-network
```

### Passo 9: Parar serviços

```bash
docker compose down
```

## Funcionamento Detalhado

### Processamento de Dados no Agregador

**1. Cálculo de Dias Ativos:**
```python
dias_ativos = (data_atual - data_criacao).days
```

**2. Classificação de Status:**
- **Veterano**: > 365 dias
- **Experiente**: > 180 dias
- **Intermediário**: > 90 dias
- **Novo**: ≤ 90 dias

**3. Geração de Resumo:**
Combina nome, role, status e dias ativos em texto legível.

### Tratamento de Erros

**ConnectionError:**
```json
{
  "error": "Unable to connect to users-service",
  "service_url": "http://servico-usuarios:5001"
}
```
HTTP Status: 503 Service Unavailable

**Timeout:**
```json
{
  "error": "Timeout connecting to users-service"
}
```
HTTP Status: 504 Gateway Timeout

**Usuário não encontrado:**
```json
{
  "error": "User not found",
  "user_id": 999
}
```
HTTP Status: 404 Not Found

## Endpoints Detalhados

### Serviço de Usuários (5001)

| Método | Endpoint | Descrição | Resposta |
|--------|----------|-----------|----------|
| GET | /users | Lista todos os usuários | JSON com array de usuários |
| GET | /users/:id | Retorna usuário específico | JSON com usuário ou 404 |
| GET | /health | Health check do serviço | Status healthy |

### Serviço Agregador (5002)

| Método | Endpoint | Descrição | Resposta |
|--------|----------|-----------|----------|
| GET | /users/summary | Lista usuários com informações agregadas | JSON enriquecido |
| GET | /users/:id/summary | Retorna usuário específico enriquecido | JSON com cálculos adicionais |
| GET | /stats | Estatísticas agregadas de todos usuários | JSON com contagens e distribuições |
| GET | /health | Health check (verifica dependências) | Status do agregador e users-service |

## Demonstração de Comunicação

Execute esta sequência para ver a comunicação em ação:

```bash
docker compose up -d
docker compose logs -f
```

Em outro terminal:
```bash
curl http://localhost:5002/users/summary
```

**Nos logs você verá:**
1. Agregador recebe requisição do cliente
2. Agregador faz requisição HTTP para usuários
3. Serviço de usuários loga requisição recebida
4. Serviço de usuários retorna dados
5. Agregador processa e enriquece dados
6. Agregador retorna resposta ao cliente

## Comparação: Dados Originais vs Enriquecidos

### Dados do Serviço de Usuários (Original)

```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao.silva@email.com",
  "role": "Developer",
  "created_at": "2024-12-02T11:00:00"
}
```

### Dados do Agregador (Enriquecidos)

```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao.silva@email.com",
  "role": "Developer",
  "created_at": "2024-12-02T11:00:00",
  "days_active": 365,
  "status": "Veterano",
  "years_active": 1.0,
  "months_active": 12.2,
  "summary": "João Silva (Developer) - Veterano - 365 dias na plataforma"
}
```

## Troubleshooting

### Agregador não consegue conectar ao serviço de usuários

Verifique se ambos estão na mesma rede:
```bash
docker network inspect desafio4-network
```

Teste conectividade:
```bash
docker exec -it servico-agregador ping servico-usuarios
docker exec -it servico-agregador curl http://servico-usuarios:5001/health
```

### Portas já em uso

Altere as portas no `docker-compose.yml`:
```yaml
ports:
  - "5003:5001"
  - "5004:5002"
```

### Serviço não inicia (unhealthy)

Verifique logs:
```bash
docker logs servico-usuarios
docker logs servico-agregador
```

Verifique health check:
```bash
docker inspect servico-usuarios --format='{{.State.Health.Status}}'
```

### Reconstruir do zero

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Conceitos Importantes

### Microsserviços
Arquitetura onde aplicação é composta por serviços pequenos, independentes e fracamente acoplados.

### Service-to-Service Communication
Comunicação direta entre microsserviços via HTTP REST, sem gateway intermediário.

### Service Discovery
Mecanismo pelo qual serviços descobrem e se comunicam entre si (neste caso, via DNS do Docker).

### Data Enrichment
Processo de adicionar informações calculadas ou agregadas aos dados originais.