FROM python:3.11-alpine

LABEL maintainer="Desafio 4 - Computação Concorrente"
LABEL description="Microsserviço de Usuários - Fornece dados de usuários"
LABEL version="1.0"

RUN apk add --no-cache curl

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5001

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

CMD ["python", "app.py"]