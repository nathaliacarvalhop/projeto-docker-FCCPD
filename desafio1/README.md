# Desafio 1: Containers em Rede

## Descrição do Projeto

Este projeto implementa uma solução de comunicação entre containers Docker utilizando uma rede customizada. O sistema consiste em dois containers independentes que se comunicam via protocolo HTTP através de uma rede bridge Docker nomeada.

### Objetivo

Demonstrar a comunicação entre containers Docker utilizando:
- Um servidor web (Flask) que expõe endpoints HTTP na porta 8080
- Um cliente que realiza requisições HTTP periódicas ao servidor
- Uma rede Docker customizada com DNS automático para resolução de nomes

## Arquitetura da Solução

### Componentes

**1. Servidor Web (servidor-web)**
- Framework: Flask (Python 3.11)
- Porta: 8080
- Função: Expõe endpoint `/health` que retorna informações sobre o status do servidor
- Imagem base: python:3.11-alpine

**2. Cliente HTTP (cliente)**
- Linguagem: Python 3.11 com biblioteca requests
- Função: Realiza requisições HTTP para o servidor a cada 5 segundos
- Imagem base: python:3.11-alpine

**3. Rede Docker**
- Nome: desafio1-network
- Tipo: bridge
- Função: Permite comunicação entre containers usando nomes de container como DNS

### Diagrama de Arquitetura

```
┌─────────────────────────────────────┐
│    Rede: desafio1-network (bridge) │
│                                     │
│  ┌──────────────┐  HTTP Request    │
│  │   cliente    │ ───────────────► │
│  │  (Python)    │                  │
│  └──────────────┘  ◄─────────────  │
│                     HTTP Response  │
│                                     │
│                    ┌──────────────┐│
│                    │servidor-web  ││
│                    │  (Flask)     ││
│                    │  Port: 8080  ││
│                    └──────────────┘│
└─────────────────────────────────────┘
         │
         └──► Host: localhost:8080
```

## Decisões Técnicas

### 1. Rede User-Defined Bridge
Optou-se por criar uma rede bridge customizada ao invés de usar a rede padrão do Docker porque apenas redes user-defined possuem DNS automático integrado. Isso permite que o cliente referencie o servidor pelo nome `servidor-web` ao invés de precisar descobrir o IP dinâmico.[8]

### 2. Imagens Alpine Linux
Utilizamos `python:3.11-alpine` como imagem base para ambos os containers, reduzindo significativamente o tamanho das imagens (aproximadamente 50MB vs 900MB de imagens Python padrão).[2]

### 3. Logging Estruturado
Implementação do módulo `logging` do Python ao invés de `print()` para:
- Captura automática de logs pelo Docker via stdout/stderr
- Formatação padronizada com timestamps
- Níveis de severidade (INFO, ERROR)
- Facilita debug e monitoramento[2]

### 4. Dependência entre Serviços
Uso de `depends_on` no Docker Compose para garantir que o cliente só inicie após o servidor estar disponível.

### 5. Política de Restart
Configuração `restart: unless-stopped` para alta disponibilidade - containers reiniciam automaticamente em caso de falha.

## Estrutura de Arquivos

```
desafio1/
├── servidor-web/
│   ├── Dockerfile              # Definição da imagem do servidor
│   ├── app.py                  # Aplicação Flask
│   └── requirements.txt        # Dependências Python (flask, werkzeug)
├── cliente/
│   ├── Dockerfile              # Definição da imagem do cliente
│   ├── cliente.py              # Script de requisições HTTP
│   └── requirements.txt        # Dependências Python (requests, urllib3)
├── docker-compose.yml          # Orquestração dos serviços
└── README.md                   # Este arquivo
```

## Tecnologias Utilizadas

- **Docker**: 20.10+ (containerização)
- **Docker Compose**: 2.0+ (orquestração)
- **Python**: 3.11 (linguagem de programação)
- **Flask**: 3.0.0 (framework web)
- **Requests**: 2.31.0 (cliente HTTP)
- **Alpine Linux**: 3.x (sistema operacional base)

## Pré-requisitos

Antes de executar o projeto, certifique-se de ter instalado:

- Docker Engine 20.10 ou superior
- Docker Compose 2.0 ou superior
- Git (para clonar o repositório)

### Verificar instalação:

```bash
docker --version
docker compose version
```

## Instruções de Execução

### Passo 1: Clonar o repositório

```bash
git clone <url-do-repositorio>
cd desafio1
```

### Passo 2: Construir e iniciar os containers

```bash
docker compose up --build
```

**Parâmetros:**
- `--build`: Força a reconstrução das imagens Docker
- Omita `-d` para ver os logs em tempo real no terminal

### Passo 3: Verificar status dos containers

Em outro terminal, execute:

```bash
docker compose ps
```

**Saída esperada:**
```
NAME            IMAGE                   STATUS          PORTS
servidor-web    desafio1-servidor-web   Up 30 seconds   0.0.0.0:8080->8080/tcp
cliente         desafio1-cliente        Up 28 seconds   
```

### Passo 4: Visualizar logs

**Logs em tempo real de ambos containers:**
```bash
docker compose logs -f
```

**Logs apenas do servidor:**
```bash
docker logs -f servidor-web
```

**Logs apenas do cliente:**
```bash
docker logs -f cliente
```

**Últimas 50 linhas dos logs:**
```bash
docker compose logs --tail=50
```

### Passo 5: Testar comunicação

**Testar endpoint externamente:**
```bash
curl http://localhost:8080/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-02T12:36:15.123456",
  "request_number": 5,
  "message": "Servidor funcionando com sucesso"
}
```

**Testar DNS interno (de dentro do container cliente):**
```bash
docker exec -it cliente ping -c 3 servidor-web
```

**Fazer requisição manual do cliente:**
```bash
docker exec -it cliente wget -O- http://servidor-web:8080/health
```

### Passo 6: Inspecionar a rede Docker

**Ver detalhes da rede:**
```bash
docker network inspect desafio1-network
```

**Ver IPs atribuídos:**
```bash
docker network inspect desafio1-network --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}'
```

### Passo 7: Parar os containers

**Parar mantendo os containers:**
```bash
docker compose stop
```

**Parar e remover containers:**
```bash
docker compose down
```

**Parar, remover containers e volumes:**
```bash
docker compose down -v
```

## Funcionamento Detalhado

### Fluxo de Comunicação

1. **Inicialização:**
   - Docker Compose cria a rede `desafio1-network`
   - Constrói as imagens dos containers a partir dos Dockerfiles
   - Inicia o container `servidor-web` na porta 8080
   - Aguarda o servidor estar pronto
   - Inicia o container `cliente`

2. **Comunicação:**
   - Cliente aguarda 3 segundos para garantir que servidor está pronto
   - Cliente faz requisição HTTP GET para `http://servidor-/health`
   - DNS do Docker resolve `servidor-web` para o IP do container
   - Servidor recebe requisição, incrementa contador e retorna JSON
   - Cliente recebe resposta e exibe log de sucesso
   - Processo se repete a cada 5 segundos

3. **Logs:**
   - Ambos containers registram cada interação
   - Servidor loga cada requisição recebida com número sequencial
   - Cliente loga cada requisição enviada e resposta recebida
   - Logs incluem timestamps para rastreabilidade

### Endpoints Disponíveis

**GET /health**
- Retorna status do servidor e contador de requisições
- Usado pelo cliente para polling periódico
- Formato de resposta: JSON

**GET /**
- Retorna informações básicas do serviço
- Lista endpoints disponíveis
- Formato de resposta: JSON

## Demonstração da Comunicação

Ao executar `docker compose logs -f`, você verá a troca de mensagens:

```
servidor-web | 2025-12-02 12:36:03,470 - INFO - Iniciando servidor Flask na porta 8080
cliente      | 2025-12-02 12:36:06,123 - INFO - Cliente iniciado - Alvo: http://servidor-web:8080/health
cliente      | 2025-12-02 12:36:06,124 - INFO - Intervalo de requisicao: 5 segundos
cliente      | 2025-12-02 12:36:09,456 - INFO - [Requisicao #1]
servidor-web | 2025-12-02 12:36:09,457 - INFO - Verificacao de saude #1 - Requisicao recebida
cliente      | 2025-12-02 12:36:09,458 - INFO - SUCESSO - Status: healthy | Requisicao #1
cliente      | 2025-12-02 12:36:14,789 - INFO - [Requisicao #2]
servidor-web | 2025-12-02 12:36:14,790 - INFO - Verificacao de saude #2 - Requisicao recebida
cliente      | 2025-12-02 12:36:14,791 - INFO - SUCESSO - Status: healthy | Requisicao #2
```

## Troubleshooting

### Container não inicia

```bash
docker compose ps
docker logs <nome-do-container>
```

### Erro de conexão entre containers

```bash
docker network inspect desafio1-network
docker exec -it cliente ping servidor-web
```

### Porta 8080 já em uso

Altere a porta no `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Usa 8081 no host
```

### Reconstruir imagens do zero

```bash
docker compose down
docker compose build --no-cache
docker compose up
```