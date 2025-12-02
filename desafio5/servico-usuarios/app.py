from flask import Flask, jsonify, request
import logging
from datetime import datetime, timedelta

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
        'phone': '(11) 98765-4321',
        'status': 'active',
        'created_at': (datetime.now() - timedelta(days=365)).isoformat()
    },
    {
        'id': 2,
        'name': 'Maria Santos',
        'email': 'maria.santos@email.com',
        'phone': '(21) 99876-5432',
        'status': 'active',
        'created_at': (datetime.now() - timedelta(days=180)).isoformat()
    },
    {
        'id': 3,
        'name': 'Pedro Oliveira',
        'email': 'pedro.oliveira@email.com',
        'phone': '(31) 91234-5678',
        'status': 'active',
        'created_at': (datetime.now() - timedelta(days=730)).isoformat()
    },
    {
        'id': 4,
        'name': 'Ana Costa',
        'email': 'ana.costa@email.com',
        'phone': '(41) 92345-6789',
        'status': 'inactive',
        'created_at': (datetime.now() - timedelta(days=90)).isoformat()
    }
]

@app.route('/users', methods=['GET'])
def get_users():
    logger.info(f"GET /users - IP: {request.remote_addr}")
    
    status_filter = request.args.get('status')
    
    if status_filter:
        filtered_users = [u for u in users_database if u['status'] == status_filter]
        return jsonify({
            'service': 'users-service',
            'filter': {'status': status_filter},
            'count': len(filtered_users),
            'users': filtered_users
        }), 200
    
    return jsonify({
        'service': 'users-service',
        'count': len(users_database),
        'users': users_database
    }), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    logger.info(f"GET /users/{user_id} - IP: {request.remote_addr}")
    
    user = next((u for u in users_database if u['id'] == user_id), None)
    
    if not user:
        return jsonify({
            'service': 'users-service',
            'error': 'User not found',
            'user_id': user_id
        }), 404
    
    return jsonify({
        'service': 'users-service',
        'user': user
    }), 200

@app.route('/users/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'users-service',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    logger.info("Iniciando Users Service na porta 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)