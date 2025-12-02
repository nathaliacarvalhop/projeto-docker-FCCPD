# Desafio 2: Volumes e Persistência

## Descrição do Projeto

Este projeto demonstra o uso de volumes Docker para persistência de dados além do ciclo de vida dos containers. A solução implementa um banco de dados SQLite gerenciado através do ORM SQLAlchemy, provando que os dados permanecem intactos mesmo após remover e recriar containers.

### Objetivo

Demonstrar persistência de dados usando volumes Docker através de:
- Banco de dados SQLite armazenado em volume nomeado
- Scripts Python com SQLAlchemy ORM para manipular dados
- Comprovação prática de que dados sobrevivem à destruição de containers

## Arquitetura da Solução

### Componentes

**1. Volume Docker (dados_sqlite)**
- Tipo: Named Volume
- Localização: Gerenciado pelo Docker
- Função: Armazena o arquivo SQLite (`desafio2.db`) de forma persistente
- Ciclo de vida: Independente dos containers

**2. Aplicação Popular (app-popular)**
- Linguagem: Python 3.11 com SQLAlchemy
- Função: Cria tabelas e insere dados iniciais no banco
- Volume montado em: `/data`

**3. Aplicação Ler (app-ler)**
- Linguagem: Python 3.11 com SQLAlchemy
- Função: Lê e exibe dados persistidos no volume
- Volume montado em: `/data`

### Diagrama de Arquitetura

```
┌─────────────────────────────────────────────┐
│   Volume: dados_sqlite (persistente)        │
│   Arquivo: /data/desafio2.db                │
│                                             │
│   ┌─────────────────────────────────┐      │
│   │  Tabela: usuarios               │      │
│   │  - id, nome, email, data_criacao│      │
│   └─────────────────────────────────┘      │
│                                             │
│   ┌─────────────────────────────────┐      │
│   │  Tabela: produtos               │      │
│   │  - id, nome, preco, estoque     │      │
│   └─────────────────────────────────┘      │
└─────────────────────────────────────────────┘
         ▲                    ▲
         │                    │
    ┌────┴─────┐         ┌────┴─────┐
    │app-popular│         │ app-ler  │
    │(escreve)  │         │  (lê)    │
    └───────────┘         └──────────┘
```

## Decisões Técnicas

### 1. SQLite vs PostgreSQL/MySQL
Optou-se por SQLite porque:
- Não requer servidor de banco de dados separado
- Arquivo único facilita demonstração de persistência
- Simples de gerenciar e inspecionar
- Ideal para demonstração didática de volumes

### 2. Named Volumes vs Bind Mounts
Utilizou-se Named Volume porque:
- **Portabilidade**: Volumes podem ser movidos entre hosts facilmente
- **Gerenciamento**: Docker gerencia automaticamente a localização
- **Performance**: Melhor desempenho que bind mounts em Windows/Mac
- **Isolamento**: Não depende de estrutura de diretórios do host

### 3. SQLAlchemy ORM
Escolha do SQLAlchemy permite:
- Abstração de banco de dados
- Código mais pythônico e legível
- Validação automática de tipos
- Migrations facilitadas (futuras extensões)

### 4. Profiles no Docker Compose
Uso de `profiles` para `app-ler` permite:
- Execução sob demanda com `docker compose run`
- Evita execução automática no `docker compose up`
- Controle fino sobre quando ler dados

## Estrutura de Arquivos

```
desafio2/
├── aplicacao/
│   ├── Dockerfile              # Imagem Python com SQLAlchemy
│   ├── models.py               # Definição dos modelos ORM
│   ├── popular.py              # Script para inserir dados
│   ├── ler.py                  # Script para ler dados
│   └── requirements.txt        # Dependências (sqlalchemy)
├── docker-compose.yml          # Orquestração dos serviços
└── README.md                   # Este arquivo
```

## Tecnologias Utilizadas

- **Docker**: 20.10+ (containerização)
- **Docker Compose**: 2.0+ (orquestração)
- **Python**: 3.11 (linguagem de programação)
- **SQLAlchemy**: 2.0.23 (ORM)
- **SQLite**: 3.x (banco de dados)
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

### Demonstração Completa de Persistência

Esta sequência demonstra que os dados sobrevivem à destruição dos containers:

#### Passo 1: Popular o banco de dados

```bash
cd desafio2
docker compose up --build app-popular
```

**Saída esperada:**
```
app-popular | Iniciando script de populacao do banco de dados
app-popular | Criando tabelas no banco de dados...
app-popular | Inserindo usuarios no banco de dados...
app-popular | Inserindo produtos no banco de dados...
app-popular | ======================================================================
app-popular | DADOS INSERIDOS COM SUCESSO!
app-popular | Usuarios inseridos nesta execucao: 5
app-popular | Produtos inseridos nesta execucao: 5
app-popular | Total de usuarios no banco: 5
app-popular | Total de produtos no banco: 5
app-popular | Arquivo do banco: /data/desafio2.db
app-popular | ======================================================================
```

#### Passo 2: Ler dados pela primeira vez

```bash
docker compose run --rm app-ler
```

**Saída esperada:**
```
app-ler | ======================================================================
app-ler | LEITURA DE DADOS PERSISTIDOS NO VOLUME
app-ler | ======================================================================
app-ler | 
app-ler | >>> USUARIOS CADASTRADOS (5 registros):
app-ler |   [ID: 1] Joao Silva - joao.silva@email.com
app-ler |   [ID: 2] Maria Santos - maria.santos@email.com
app-ler |   [ID: 3] Pedro Oliveira - pedro.oliveira@email.com
app-ler |   [ID: 4] Ana Costa - ana.costa@email.com
app-ler |   [ID: 5] Carlos Souza - carlos.souza@email.com
app-ler | 
app-ler | >>> PRODUTOS CADASTRADOS (5 registros):
app-ler |   [ID: 1] Notebook Dell - R$ 3500.00 | Estoque: 10
app-ler |   [ID: 2] Mouse Logitech - R$ 85.50 | Estoque: 50
app-ler | ======================================================================
app-ler | COMPROVACAO: Dados foram recuperados do volume persistente!
app-ler | ======================================================================
```

#### Passo 3: **DESTRUIR** o container que populou os dados

```bash
docker rm -f app-popular
docker ps -a
```

**Resultado:** Container foi completamente removido.

#### Passo 4: **COMPROVAR PERSISTÊNCIA** - Ler dados novamente

```bash
docker compose run --rm app-ler
```

**Resultado:** **Os dados continuam lá!** Mesmo após destruir o container original, os dados persistem no volume.

#### Passo 5: Popular novamente (testar comportamento de duplicação)

```bash
docker compose up app-popular
```

**Observe:** 
- Usuários não são duplicados (constraint UNIQUE no email)
- Produtos são inseridos novamente (sem constraint)

#### Passo 6: Verificar contagem final

```bash
docker compose run --rm app-ler
```

**Resultado:** Agora há 10 produtos (5 originais + 5 novos) mas apenas 5 usuários.

### Comandos Adicionais

#### Inspecionar o volume criado

```bash
docker volume ls
docker volume inspect desafio2_dados_sqlite
```

**Saída do inspect:**
```json
[
    {
        "CreatedAt": "2025-12-02T10:30:00Z",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "desafio2",
            "com.docker.compose.volume": "dados_sqlite"
        },
        "Mountpoint": "/var/lib/docker/volumes/desafio2_dados_sqlite/_data",
        "Name": "desafio2_dados_sqlite",
        "Options": null,
        "Scope": "local"
    }
]
```

#### Ver localização física do volume

```bash
docker volume inspect desafio2_dados_sqlite --format '{{.Mountpoint}}'
```

#### Acessar shell dentro do container para explorar

```bash
docker compose run --rm app-ler sh
ls -lh /data
cat /data/desafio2.db
exit
```

#### Limpar ambiente completamente

**Remover containers e rede (mantém volume):**
```bash
docker compose down
```

**Remover tudo incluindo volumes:**
```bash
docker compose down -v
docker volume rm desafio2_dados_sqlite
```

#### Verificar espaço usado pelo volume

```bash
docker system df -v
```

## Funcionamento Detalhado

### Fluxo de Persistência

1. **Primeira Execução - Popular:**
   - Docker Compose cria volume nomeado `desafio2_dados_sqlite`
   - Container `app-popular` inicia e monta volume em `/data`
   - SQLAlchemy cria arquivo `/data/desafio2.db`
   - Script cria tabelas e insere dados
   - Container finaliza, mas volume permanece

2. **Leitura de Dados:**
   - Novo container `app-ler` monta o mesmo volume em `/data`
   - SQLAlchemy conecta ao arquivo existente
   - Script lê dados persistidos
   - Container finaliza, volume permanece intacto

3. **Destruição e Recriação:**
   - Remoção de containers não afeta o volume
   - Novos containers montam o mesmo volume
   - Dados permanecem acessíveis
   - **Isso comprova a persistência!**

### Modelos de Dados

**Tabela usuarios:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `nome` (VARCHAR 100, NOT NULL)
- `email` (VARCHAR 100, UNIQUE, NOT NULL)
- `data_criacao` (DATETIME, DEFAULT NOW)

**Tabela produtos:**
- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `nome` (VARCHAR 100, NOT NULL)
- `preco` (FLOAT, NOT NULL)
- `estoque` (INTEGER, DEFAULT 0)
- `data_criacao` (DATETIME, DEFAULT NOW)

## Comprovação da Persistência

### Teste Prático

Execute esta sequência completa para comprovar:

```bash
docker compose up --build app-popular
docker compose run --rm app-ler

docker rm -f app-popular
docker volume ls | findstr desafio2

docker compose run --rm app-ler
```

**Esperado:** Dados permanecem mesmo após remover todos os containers!

### Por que os dados persistem?

Os volumes Docker são armazenados no host e gerenciados pelo Docker Engine:
- Localização típica Linux: `/var/lib/docker/volumes/`
- Independentes do ciclo de vida dos containers
- Podem ser compartilhados entre múltiplos containers
- Sobrevivem a `docker rm` e `docker compose down`
- Apenas removidos com `docker compose down -v` ou `docker volume rm`

## Troubleshooting

### Volume não foi criado

```bash
docker volume ls
docker compose up app-popular
docker volume ls
```

### Dados não aparecem após recriar container

Verifique se o mesmo volume está sendo montado:
```bash
docker inspect app-ler --format '{{.Mounts}}'
```

### Erro de permissão no volume

```bash
docker compose run --rm app-ler ls -la /data
```

### Remover volume e recomeçar do zero

```bash
docker compose down -v
docker volume rm desafio2_dados_sqlite
docker compose up --build app-popular
```