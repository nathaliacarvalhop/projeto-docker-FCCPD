FROM python:3.11-alpine

LABEL maintainer="Desafio 2 - Computação Concorrente"
LABEL description="Aplicacao Python com SQLAlchemy e SQLite"
LABEL version="1.0"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY models.py .
COPY popular.py .
COPY ler.py .

CMD ["python", "popular.py"]