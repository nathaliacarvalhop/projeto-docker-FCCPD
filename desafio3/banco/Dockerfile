FROM postgres:16-alpine

LABEL maintainer="Desafio 3 - Computação Concorrente"
LABEL description="PostgreSQL com schema inicial de tarefas"
LABEL version="1.0"

COPY init.sql /docker-entrypoint-initdb.d/

ENV POSTGRES_DB=tasks_db
ENV POSTGRES_USER=admin
ENV POSTGRES_PASSWORD=admin123