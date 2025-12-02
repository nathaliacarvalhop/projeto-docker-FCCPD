FROM python:3.11-alpine

LABEL maintainer="Desafio 1 - Computação Concorrente"
LABEL description="Servidor Web Flask para comunicação entre containers"
LABEL version="1.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

CMD ["python", "app.py"]