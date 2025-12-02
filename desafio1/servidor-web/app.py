from flask import Flask, jsonify
from datetime import datetime
import logging

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

request_counter = 0

@app.route('/health', methods=['GET'])
def health():
    global request_counter
    request_counter += 1
    
    response = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'request_number': request_counter,
        'message': 'Servidor funcionando com sucesso'
    }
    
    logger.info(f"Verificacao de saude #{request_counter} - Requisicao recebida")
    return jsonify(response), 200

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Servidor Flask',
        'version': '1.0',
        'endpoints': ['/health', '/']
    }), 200

if __name__ == '__main__':
    logger.info("Iniciando servidor Flask na porta 8080")
    app.run(host='0.0.0.0', port=8080, debug=False)