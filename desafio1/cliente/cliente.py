import requests
import time
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SERVER_URL = "http://servidor-web:8080/health"
REQUEST_INTERVAL = 5

def make_request():
    try:
        response = requests.get(SERVER_URL, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(
                f"SUCESSO - Status: {data['status']} | "
                f"Requisicao #{data['request_number']} | "
                f"Timestamp: {data['timestamp']}"
            )
            return True
        else:
            logger.error(f"ERRO - HTTP {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("ERRO DE CONEXAO - Nao foi possivel alcançar o servidor")
        return False
    except requests.exceptions.Timeout:
        logger.error("TIMEOUT - Servidor nao respondeu a tempo")
        return False
    except Exception as e:
        logger.error(f"ERRO INESPERADO - {str(e)}")
        return False

def main():
    logger.info(f"Cliente iniciado - Alvo: {SERVER_URL}")
    logger.info(f"Intervalo de requisicao: {REQUEST_INTERVAL} segundos")
    logger.info("=" * 70)
    
    request_count = 0
    
    logger.info("Aguardando servidor estar pronto...")
    time.sleep(3)
    
    while True:
        try:
            request_count += 1
            logger.info(f"[Requisicao #{request_count}]")
            make_request()
            time.sleep(REQUEST_INTERVAL)
            
        except KeyboardInterrupt:
            logger.info("Cliente interrompido pelo usuario")
            sys.exit(0)

if __name__ == "__main__":
    main()