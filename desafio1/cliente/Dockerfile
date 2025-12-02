FROM python:3.11-alpine

LABEL maintainer="Desafio 1 - Computação Concorrente"
LABEL description="Cliente HTTP para realizar requisições periódicas"
LABEL version="1.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY cliente.py .

CMD ["python", "cliente.py"]