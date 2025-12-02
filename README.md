# Atividade Docker - Computação Concorrente, Paralela e Distribuída

Repositório contendo a implementação completa dos 5 desafios propostos na disciplina de Computação Concorrente, Paralela e Distribuída, focados em Docker, Docker Compose e arquitetura de microsserviços.

## 📋 Sobre o Projeto

Este repositório apresenta soluções práticas para desafios de containerização e orquestração de serviços, progredindo desde conceitos básicos de comunicação entre containers até arquiteturas completas de microsserviços com API Gateway.

## 🏗️ Estrutura do Repositório

```
atividade-docker/
├── desafio1/          # Containers em Rede
├── desafio2/          # Volumes e Persistência
├── desafio3/          # Docker Compose Orquestrando Serviços
├── desafio4/          # Microsserviços Independentes
├── desafio5/          # Microsserviços com API Gateway
└── README.md          # Este arquivo
```

## 🎯 Desafios Implementados

### Desafio 1 - Containers em Rede
**Conceito:** Comunicação entre containers via rede Docker customizada

**Tecnologias:** Flask, Python, Docker Networks

**Pontos-chave:**
- Rede bridge customizada com DNS automático
- Servidor web Flask (porta 8080)
- Cliente HTTP fazendo requisições periódicas
- Logs estruturados demonstrando comunicação

[📖 Ver documentação completa](./desafio1/README.md)

***

### Desafio 2 - Volumes e Persistência
**Conceito:** Persistência de dados além do ciclo de vida dos containers

**Tecnologias:** SQLite, SQLAlchemy ORM, Docker Volumes

**Pontos-chave:**
- Volume nomeado para armazenamento persistente
- Banco de dados SQLite com ORM
- Scripts para popular e ler dados
- Comprovação prática: dados sobrevivem à destruição de containers

[📖 Ver documentação completa](./desafio2/README.md)

***

### Desafio 3 - Docker Compose Orquestrando Serviços
**Conceito:** Orquestração de múltiplos serviços interdependentes

**Tecnologias:** Flask, PostgreSQL, Redis, Docker Compose

**Pontos-chave:**
- API REST para gerenciamento de tarefas
- PostgreSQL para persistência
- Redis para cache (cache-aside pattern)
- Health checks e dependências entre serviços
- Variáveis de ambiente para configuração

[📖 Ver documentação completa](./desafio3/README.md)

***

### Desafio 4 - Microsserviços Independentes
**Conceito:** Comunicação HTTP entre microsserviços

**Tecnologias:** Flask, Python Requests, Docker

**Pontos-chave:**
- Microsserviço A: fornece dados de usuários
- Microsserviço B: consome e enriquece dados (agrega informações calculadas)
- Comunicação via HTTP REST
- Service discovery via DNS do Docker
- Dockerfiles separados para isolamento

[📖 Ver documentação completa](./desafio4/README.md)

***

### Desafio 5 - Microsserviços com API Gateway
**Conceito:** Arquitetura com gateway centralizando acesso aos microsserviços

**Tecnologias:** Nginx, Flask, Docker Compose

**Pontos-chave:**
- API Gateway (Nginx) como ponto único de entrada
- Roteamento baseado em path (`/users`, `/orders`)
- Microsserviços backend não expostos externamente
- Reverse proxy com upstreams
- Abstração e isolamento de serviços

[📖 Ver documentação completa](./desafio5/README.md)

***

## 🚀 Como Executar

### Pré-requisitos

- Docker Engine 20.10+
- Docker Compose 2.0+

```bash
docker --version
docker compose version
```

### Executar um desafio específico

```bash
cd desafio1
docker compose up --build -d
docker compose ps
docker compose logs -f
```

### Parar serviços

```bash
docker compose down
docker compose down -v
```

## 📊 Progressão de Conceitos

| Desafio | Conceitos Principais |
|---------|---------------------|
| 1 | Redes Docker, DNS, comunicação HTTP básica |
| 2 | Volumes, persistência, ORM |
| 3 | Orquestração, dependências, cache, health checks |
| 4 | Microsserviços, comunicação inter-serviços, agregação de dados |
| 5 | API Gateway, reverse proxy, roteamento, isolamento |

## 🛠️ Tecnologias Utilizadas

- **Containerização:** Docker, Docker Compose
- **Backend:** Python 3.11, Flask
- **Bancos de Dados:** SQLite, PostgreSQL
- **Cache:** Redis
- **Gateway:** Nginx
- **ORM:** SQLAlchemy
- **HTTP Client:** Requests
- **Base OS:** Alpine Linux

## 📝 Padrões e Boas Práticas Aplicados

- ✅ Código em inglês, mensagens ao usuário em português
- ✅ Dockerfiles multi-stage quando aplicável
- ✅ Health checks em todos os serviços
- ✅ Logging estruturado com timestamps
- ✅ Variáveis de ambiente para configuração
- ✅ Tratamento de erros robusto
- ✅ Documentação detalhada em cada desafio
- ✅ Named volumes para persistência
- ✅ Redes customizadas para isolamento
- ✅ Restart policies para alta disponibilidade

## 📚 Documentação Individual

Cada desafio possui sua própria documentação completa incluindo:

- Descrição da solução e arquitetura
- Decisões técnicas justificadas
- Diagramas de comunicação
- Instruções passo a passo de execução
- Exemplos de uso com curl
- Troubleshooting
- Explicação do funcionamento interno

## 🎓 Objetivos de Aprendizado

Este projeto demonstra conhecimento prático em:

1. **Containerização:** Criação de imagens Docker otimizadas
2. **Orquestração:** Uso de Docker Compose para múltiplos serviços
3. **Redes:** Comunicação entre containers via DNS
4. **Persistência:** Uso correto de volumes Docker
5. **Microsserviços:** Arquitetura distribuída com serviços independentes
6. **API Gateway:** Padrão de design para centralizar acesso
7. **DevOps:** Health checks, logging, restart policies