FROM python:3.11-alpine

LABEL maintainer="Desafio 5 - Computação Concorrente"
LABEL description="Microsserviço de Pedidos"
LABEL version="1.0"

RUN apk add --no-cache curl

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5002

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/orders/health || exit 1

CMD ["python", "app.py"]