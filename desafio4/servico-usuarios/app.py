from flask import Flask, jsonify
import logging
from datetime import datetime, timedelta
import random

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

users_database = [
    {
        'id': 1,
        'name': 'João Silva',
        'email': 'joao.silva@email.com',
        'role': 'Developer',
        'created_at': (datetime.now() - timedelta(days=365)).isoformat()
    },
    {
        'id': 2,
        'name': 'Maria Santos',
        'email': 'maria.santos@email.com',
        'role': 'Designer',
        'created_at': (datetime.now() - timedelta(days=180)).isoformat()
    },
    {
        'id': 3,
        'name': 'Pedro Oliveira',
        'email': 'pedro.oliveira@email.com',
        'role': 'Manager',
        'created_at': (datetime.now() - timedelta(days=730)).isoformat()
    },
    {
        'id': 4,
        'name': 'Ana Costa',
        'email': 'ana.costa@email.com',
        'role': 'Developer',
        'created_at': (datetime.now() - timedelta(days=90)).isoformat()
    },
    {
        'id': 5,
        'name': 'Carlos Souza',
        'email': 'carlos.souza@email.com',
        'role': 'QA Engineer',
        'created_at': (datetime.now() - timedelta(days=450)).isoformat()
    }
]

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Users Microservice',
        'version': '1.0',
        'endpoints': {
            'users': '/users',
            'user_by_id': '/users/<id>',
            'health': '/health'
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'users-service',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/users', methods=['GET'])
def get_users():
    logger.info(f"Requisicao recebida: GET /users")
    
    return jsonify({
        'service': 'users-service',
        'count': len(users_database),
        'users': users_database
    }), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    logger.info(f"Requisicao recebida: GET /users/{user_id}")
    
    user = next((u for u in users_database if u['id'] == user_id), None)
    
    if not user:
        return jsonify({
            'error': 'User not found',
            'user_id': user_id
        }), 404
    
    return jsonify({
        'service': 'users-service',
        'user': user
    }), 200

if __name__ == '__main__':
    logger.info("Iniciando Users Microservice na porta 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)