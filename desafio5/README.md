# Desafio 5: Microsserviços com API Gateway

## Descrição do Projeto

Este projeto implementa uma arquitetura completa de microsserviços utilizando o padrão API Gateway. Um gateway Nginx atua como ponto único de entrada, roteando requisições para dois microsserviços backend independentes (usuários e pedidos). Esta arquitetura demonstra separação de responsabilidades, isolamento de serviços, roteamento centralizado e abstração da complexidade interna.

### Objetivo

Demonstrar arquitetura de microsserviços com API Gateway através de:
- Gateway como ponto único de entrada (single entry point)
- Microsserviço 1: Fornece dados de usuários
- Microsserviço 2: Fornece dados de pedidos
- Roteamento baseado em path (`/users` → users service, `/orders` → orders service)
- Serviços backend não expostos externamente (apenas na rede interna)
- Orquestração completa via Docker Compose

## Arquitetura da Solução

### Componentes

**1. API Gateway (gateway)**
- Tecnologia: Nginx
- Porta: 8080 (única porta exposta externamente)
- Função: Reverse proxy que roteia requisições para serviços backend
- Roteamento: `/users/*` → servico-usuarios:5001, `/orders/*` → servico-pedidos:5002

**2. Serviço de Usuários (servico-usuarios)**
- Framework: Flask (Python 3.11)
- Porta: 5001 (apenas interna, não exposta ao host)
- Função: Gerencia dados de usuários
- Endpoints: `/users`, `/users/<id>`, `/users/health`

**3. Serviço de Pedidos (servico-pedidos)**
- Framework: Flask (Python 3.11)
- Porta: 5002 (apenas interna, não exposta ao host)
- Função: Gerencia dados de pedidos
- Endpoints: `/orders`, `/orders/<id>`, `/orders/stats`, `/orders/health`

### Diagrama de Arquitetura

```
                        Cliente HTTP
                             │
                             ▼
                    ┌─────────────────┐
                    │   API GATEWAY   │
                    │   (Nginx:8080)  │
                    │  Ponto único de │
                    │     entrada     │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
    /users/* │        /orders/* │        /health │
            ▼                ▼                ▼
┌─────────────────────────────────────────────────────┐
│        Rede: desafio5-network (bridge)              │
│                                                     │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │ servico-usuarios │      │ servico-pedidos  │   │
│  │   Port: 5001     │      │   Port: 5002     │   │
│  │   (não exposto)  │      │   (não exposto)  │   │
│  │                  │      │                  │   │
│  │  GET /users      │      │  GET /orders     │   │
│  │  GET /users/:id  │      │  GET /orders/:id │   │
│  │  GET /users/health│     │  GET /orders/stats│  │
│  └──────────────────┘      └──────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘

Acesso externo APENAS via Gateway (localhost:8080)
Serviços backend ISOLADOS na rede interna
```

### Fluxo de Requisições

```
Cliente faz: GET http://localhost:8080/users
    │
    ▼
API Gateway (Nginx)
    │
    ├─► Analisa path: /users
    ├─► Consulta upstream: users_service
    ├─► Proxy para: http://servico-usuarios:5001/users
    │
    ▼
Serviço de Usuários
    │
    ▼
Retorna JSON
    │
    ▼
Gateway repassa ao cliente

─────────────────────────────────────────────

Cliente faz: GET http://localhost:8080/orders
    │
    ▼
API Gateway (Nginx)
    │
    ├─► Analisa path: /orders
    ├─► Consulta upstream: orders_service
    ├─► Proxy para: http://servico-pedidos:5002/orders
    │
    ▼
Serviço de Pedidos
    │
    ▼
Retorna JSON
    │
    ▼
Gateway repassa ao cliente
```

## Decisões Técnicas

### 1. Nginx como API Gateway
Escolha do Nginx porque:
- Alta performance e baixo consumo de recursos
- Reverse proxy robusto e maduro
- Balanceamento de carga nativo
- Configuração declarativa simples
- Amplamente usado em produção

### 2. Padrão API Gateway
Implementação do padrão para:
- **Single Entry Point**: Cliente interage apenas com gateway
- **Abstração**: Complexidade interna oculta do cliente
- **Roteamento centralizado**: Lógica de roteamento em um único lugar
- **Segurança**: Serviços backend não expostos diretamente
- **Evolução independente**: Serviços podem mudar sem afetar clientes

### 3. Exposição Seletiva de Portas
Apenas gateway exposto ao host (`ports`), serviços backend usam `expose`:
- **Segurança**: Backend inacessível diretamente de fora
- **Isolamento**: Apenas comunicação via gateway permitida
- **Controle**: Todo tráfego passa por ponto centralizado

### 4. Upstreams do Nginx
Definição de upstreams para cada serviço:
- Facilita balanceamento de carga (múltiplas instâncias)
- Permite health checks
- Configuração centralizada de backends

### 5. Proxy Headers
Gateway envia headers de contexto para backends:
- `X-Real-IP`: IP original do cliente
- `X-Forwarded-For`: Chain de proxies
- `X-Forwarded-Proto`: Protocolo original (HTTP/HTTPS)
- Permite backends logarem informações corretas

## Estrutura de Arquivos

```
desafio5/
├── gateway/
│   ├── Dockerfile              # Imagem Nginx customizada
│   └── nginx.conf              # Configuração de roteamento
├── servico-usuarios/
│   ├── Dockerfile              # Imagem Python com Flask
│   ├── app.py                  # API REST de usuários
│   └── requirements.txt        # Dependências (flask, werkzeug)
├── servico-pedidos/
│   ├── Dockerfile              # Imagem Python com Flask
│   ├── app.py                  # API REST de pedidos
│   └── requirements.txt        # Dependências (flask, werkzeug)
├── docker-compose.yml          # Orquestração dos 3 serviços
└── README.md                   # Este arquivo
```

## Tecnologias Utilizadas

- **Docker**: 20.10+ (containerização)
- **Docker Compose**: 2.0+ (orquestração)
- **Nginx**: Alpine (API Gateway / Reverse Proxy)
- **Python**: 3.11 (linguagem dos microsserviços)
- **Flask**: 3.0.0 (framework web)
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
cd desafio5
docker compose up --build -d
```

**Ordem de inicialização:**
1. `servico-usuarios` e `servico-pedidos` iniciam primeiro
2. Health checks verificam se estão healthy
3. `gateway` inicia por último (depende dos backends estarem saudáveis)

### Passo 2: Verificar status dos serviços

```bash
docker compose ps
```

**Saída esperada:**
```
NAME                IMAGE                     STATUS         PORTS
gateway             desafio5-gateway          Up (healthy)   0.0.0.0:8080->8080/tcp
servico-usuarios    desafio5-servico-usuarios Up (healthy)   5001/tcp
servico-pedidos     desafio5-servico-pedidos  Up (healthy)   5002/tcp
```

**Observe:** Apenas gateway tem portas expostas ao host!

### Passo 3: Testar API Gateway

#### Endpoint raiz do gateway

```bash
curl http://localhost:8080/
```

**Resposta:**
```json
{
  "service": "API Gateway",
  "version": "1.0",
  "endpoints": {
    "/users": "Users Service",
    "/orders": "Orders Service",
    "/health": "Gateway Health"
  }
}
```

#### Health check do gateway

```bash
curl http://localhost:8080/health
```

### Passo 4: Acessar Serviço de Usuários via Gateway

**IMPORTANTE:** Acesso direto a `localhost:5001` NÃO funciona (porta não exposta). Apenas via gateway!

#### Listar todos os usuários

```bash
curl http://localhost:8080/users
```

**Resposta:**
```json
{
  "service": "users-service",
  "count": 4,
  "users": [
    {
      "id": 1,
      "name": "João Silva",
      "email": "joao.silva@email.com",
      "phone": "(11) 98765-4321",
      "status": "active",
      "created_at": "2024-12-02T11:00:00.000000"
    },
    ...
  ]
}
```

#### Buscar usuário específico

```bash
curl http://localhost:8080/users/1
```

#### Filtrar usuários por status

```bash
curl "http://localhost:8080/users?status=active"
```

### Passo 5: Acessar Serviço de Pedidos via Gateway

#### Listar todos os pedidos

```bash
curl http://localhost:8080/orders
```

**Resposta:**
```json
{
  "service": "orders-service",
  "count": 5,
  "total_value": 6221.00,
  "orders": [
    {
      "id": 1001,
      "user_id": 1,
      "product": "Notebook Dell",
      "quantity": 1,
      "total": 3500.00,
      "status": "delivered",
      "created_at": "2025-11-02T11:00:00.000000"
    },
    ...
  ]
}
```

#### Buscar pedido específico

```bash
curl http://localhost:8080/orders/1001
```

#### Filtrar pedidos por usuário

```bash
curl "http://localhost:8080/orders?user_id=1"
```

#### Filtrar pedidos por status

```bash
curl "http://localhost:8080/orders?status=delivered"
```

#### Obter estatísticas de pedidos

```bash
curl http://localhost:8080/orders/stats
```

**Resposta:**
```json
{
  "service": "orders-service",
  "total_orders": 5,
  "total_revenue": 6221.00,
  "average_order_value": 1244.20,
  "orders_by_status": {
    "delivered": 2,
    "shipped": 1,
    "processing": 1,
    "pending": 1
  },
  "timestamp": "2025-12-02T11:50:00.000000"
}
```

### Passo 6: Demonstrar Isolamento dos Serviços Backend

Tente acessar serviços diretamente (deve falhar):

```bash
curl http://localhost:5001/users
curl http://localhost:5002/orders
```

**Resultado:** `Connection refused` ou `Connection error`

**Motivo:** Portas 5001 e 5002 não estão expostas ao host, apenas internamente na rede Docker!

### Passo 7: Visualizar logs

**Logs do gateway (Nginx):**
```bash
docker logs -f gateway
```

**Logs dos serviços:**
```bash
docker logs -f servico-usuarios
docker logs -f servico-pedidos
```

**Todos simultaneamente:**
```bash
docker compose logs -f
```

### Passo 8: Ver logs de acesso do Nginx

```bash
docker exec -it gateway cat /var/log/nginx/access.log
```

### Passo 9: Testar roteamento nos logs

Execute requisições e veja o roteamento:

```bash
curl http://localhost:8080/users
curl http://localhost:8080/orders
docker compose logs --tail=30
```

**Você verá:**
```
gateway           | 172.18.0.1 - - [02/Dec/2025:11:50:00] "GET /users HTTP/1.1" 200
servico-usuarios  | GET /users - IP: 172.18.0.4
gateway           | 172.18.0.1 - - [02/Dec/2025:11:50:05] "GET /orders HTTP/1.1" 200
servico-pedidos   | GET /orders - IP: 172.18.0.4
```

### Passo 10: Inspecionar rede Docker

```bash
docker network inspect desafio5-network
```

### Passo 11: Parar serviços

```bash
docker compose down
```

## Funcionamento Detalhado

### Configuração de Roteamento no Nginx

**Upstream Definitions:**
```nginx
upstream users_service {
    server servico-usuarios:5001;
}

upstream orders_service {
    server servico-pedidos:5002;
}
```

**Location Blocks:**
```nginx
location /users {
    proxy_pass http://users_service;
    # Headers e configurações de proxy
}

location /orders {
    proxy_pass http://orders_service;
    # Headers e configurações de proxy
}
```

### Vantagens da Arquitetura API Gateway

**1. Single Entry Point**
- Cliente conhece apenas um endpoint (gateway:8080)
- Simplifica configuração do lado do cliente
- Facilita mudanças na infraestrutura backend

**2. Abstração**
- Clientes não conhecem detalhes internos
- Serviços podem ser movidos/escalados sem afetar clientes
- Múltiplas instâncias de serviços transparentes para clientes

**3. Segurança**
- Backends não expostos diretamente à internet
- Gateway pode implementar autenticação/autorização
- Rate limiting centralizado
- Validação de requisições

**4. Cross-Cutting Concerns**
- Logging centralizado
- CORS headers
- Compression
- SSL/TLS termination
- Request/Response transformation

**5. Evolução Independente**
- Adicionar novos serviços sem alterar clientes
- Versionar APIs facilmente
- A/B testing e canary deployments

## Endpoints Disponíveis

### Via API Gateway (localhost:8080)

| Path | Destino | Descrição |
|------|---------|-----------|
| GET / | Gateway | Informações do gateway |
| GET /health | Gateway | Health check do gateway |
| GET /users | servico-usuarios:5001 | Lista todos os usuários |
| GET /users/:id | servico-usuarios:5001 | Retorna usuário específico |
| GET /users?status=:status | servico-usuarios:5001 | Filtra usuários por status |
| GET /orders | servico-pedidos:5002 | Lista todos os pedidos |
| GET /orders/:id | servico-pedidos:5002 | Retorna pedido específico |
| GET /orders?user_id=:id | servico-pedidos:5002 | Filtra pedidos por usuário |
| GET /orders?status=:status | servico-pedidos:5002 | Filtra pedidos por status |
| GET /orders/stats | servico-pedidos:5002 | Estatísticas de pedidos |

## Comparação: Com vs Sem API Gateway

### Sem API Gateway (Acesso Direto)

```
Cliente → servico-usuarios:5001
Cliente → servico-pedidos:5002
Cliente → servico-produtos:5003
...

Problemas:
- Cliente precisa conhecer múltiplos endpoints
- Serviços expostos diretamente
- Difícil adicionar autenticação
- Difícil implementar rate limiting
```

### Com API Gateway (Este Projeto)

```
Cliente → gateway:8080 → servico-usuarios:5001
Cliente → gateway:8080 → servico-pedidos:5002

Vantagens:
- Cliente conhece apenas gateway
- Serviços isolados na rede interna
- Autenticação/autorização centralizada
- Rate limiting no gateway
- Logging e monitoramento centralizados
```

## Troubleshooting

### Gateway não consegue rotear para serviços

Verifique se serviços estão healthy:
```bash
docker compose ps
docker logs servico-usuarios
docker logs servico-pedidos
```

Teste conectividade interna:
```bash
docker exec -it gateway ping servico-usuarios
docker exec -it gateway ping servico-pedidos
```

### Erro 502 Bad Gateway

Significa que gateway não consegue alcançar backend:
```bash
docker logs gateway
docker compose restart servico-usuarios servico-pedidos
```

### Erro 503 Service Unavailable

Backend está down ou não está healthy:
```bash
docker compose ps
docker compose up -d servico-usuarios servico-pedidos
```

### Porta 8080 já em uso

Altere no `docker-compose.yml`:
```yaml
gateway:
  ports:
    - "8081:8080"
```

Acesse via `http://localhost:8081`

### Reconstruir completamente

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Conceitos Importantes

### API Gateway Pattern
Padrão arquitetural onde um único ponto de entrada roteia requisições para múltiplos microsserviços backend.

### Reverse Proxy
Servidor que encaminha requisições de clientes para servidores backend apropriados.

### Backend for Frontend (BFF)
Variação do API Gateway onde cada tipo de cliente (web, mobile, etc) tem seu próprio gateway.

### Service Mesh
Evolução do API Gateway com recursos avançados de roteamento, observabilidade e segurança (ex: Istio, Linkerd).