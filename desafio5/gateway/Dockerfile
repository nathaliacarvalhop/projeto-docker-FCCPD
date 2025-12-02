FROM nginx:alpine

LABEL maintainer="Desafio 5 - Computação Concorrente"
LABEL description="API Gateway usando Nginx"
LABEL version="1.0"

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1