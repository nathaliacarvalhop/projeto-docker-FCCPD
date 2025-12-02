from flask import Flask, jsonify
import logging
import requests
from datetime import datetime
import os

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

USERS_SERVICE_URL = os.getenv('USERS_SERVICE_URL', 'http://servico-usuarios:5001')

def calculate_days_active(created_at_str):
    try:
        created_date = datetime.fromisoformat(created_at_str)
        days_active = (datetime.now() - created_date).days
        return days_active
    except Exception as e:
        logger.error(f"Erro ao calcular dias ativos: {str(e)}")
        return 0

def get_status_badge(days_active):
    if days_active > 365:
        return 'Veterano'
    elif days_active > 180:
        return 'Experiente'
    elif days_active > 90:
        return 'Intermediario'
    else:
        return 'Novo'

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Aggregator Microservice',
        'version': '1.0',
        'description': 'Consome users-service e adiciona informacoes agregadas',
        'endpoints': {
            'users_summary': '/users/summary',
            'user_summary': '/users/<id>/summary',
            'stats': '/stats',
            'health': '/health'
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    try:
        response = requests.get(f"{USERS_SERVICE_URL}/health", timeout=3)
        users_service_status = 'healthy' if response.status_code == 200 else 'unhealthy'
    except:
        users_service_status = 'unreachable'
    
    return jsonify({
        'status': 'healthy',
        'service': 'aggregator-service',
        'dependencies': {
            'users-service': users_service_status
        },
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/users/summary', methods=['GET'])
def get_users_summary():
    try:
        logger.info(f"Chamando servico de usuarios: {USERS_SERVICE_URL}/users")
        
        response = requests.get(f"{USERS_SERVICE_URL}/users", timeout=5)
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to fetch users from users-service',
                'status_code': response.status_code
            }), 502
        
        users_data = response.json()
        users = users_data.get('users', [])
        
        enriched_users = []
        for user in users:
            days_active = calculate_days_active(user['created_at'])
            status_badge = get_status_badge(days_active)
            
            enriched_user = {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'created_at': user['created_at'],
                'days_active': days_active,
                'status': status_badge,
                'summary': f"{user['name']} ({user['role']}) - {status_badge} - {days_active} dias na plataforma"
            }
            enriched_users.append(enriched_user)
        
        logger.info(f"Processados {len(enriched_users)} usuarios com informacoes agregadas")
        
        return jsonify({
            'service': 'aggregator-service',
            'source': 'users-service',
            'count': len(enriched_users),
            'users': enriched_users
        }), 200
    
    except requests.exceptions.ConnectionError:
        logger.error("Erro de conexao com users-service")
        return jsonify({
            'error': 'Unable to connect to users-service',
            'service_url': USERS_SERVICE_URL
        }), 503
    
    except requests.exceptions.Timeout:
        logger.error("Timeout ao conectar com users-service")
        return jsonify({
            'error': 'Timeout connecting to users-service'
        }), 504
    
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/users/<int:user_id>/summary', methods=['GET'])
def get_user_summary(user_id):
    try:
        logger.info(f"Chamando servico de usuarios: {USERS_SERVICE_URL}/users/{user_id}")
        
        response = requests.get(f"{USERS_SERVICE_URL}/users/{user_id}", timeout=5)
        
        if response.status_code == 404:
            return jsonify({
                'error': 'User not found',
                'user_id': user_id
            }), 404
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to fetch user from users-service',
                'status_code': response.status_code
            }), 502
        
        user_data = response.json()
        user = user_data.get('user', {})
        
        days_active = calculate_days_active(user['created_at'])
        status_badge = get_status_badge(days_active)
        
        enriched_user = {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'created_at': user['created_at'],
            'days_active': days_active,
            'status': status_badge,
            'years_active': round(days_active / 365, 1),
            'months_active': round(days_active / 30, 1),
            'summary': f"{user['name']} ({user['role']}) - {status_badge} - {days_active} dias na plataforma"
        }
        
        logger.info(f"Usuario {user_id} processado com informacoes agregadas")
        
        return jsonify({
            'service': 'aggregator-service',
            'source': 'users-service',
            'user': enriched_user
        }), 200
    
    except requests.exceptions.ConnectionError:
        logger.error("Erro de conexao com users-service")
        return jsonify({
            'error': 'Unable to connect to users-service'
        }), 503
    
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    try:
        response = requests.get(f"{USERS_SERVICE_URL}/users", timeout=5)
        
        if response.status_code != 200:
            return jsonify({
                'error': 'Failed to fetch users'
            }), 502
        
        users_data = response.json()
        users = users_data.get('users', [])
        
        total_users = len(users)
        
        status_counts = {
            'Veterano': 0,
            'Experiente': 0,
            'Intermediario': 0,
            'Novo': 0
        }
        
        role_counts = {}
        
        for user in users:
            days_active = calculate_days_active(user['created_at'])
            status = get_status_badge(days_active)
            status_counts[status] += 1
            
            role = user.get('role', 'Unknown')
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return jsonify({
            'service': 'aggregator-service',
            'total_users': total_users,
            'users_by_status': status_counts,
            'users_by_role': role_counts,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Erro ao gerar estatisticas: {str(e)}")
        return jsonify({
            'error': 'Failed to generate stats',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Iniciando Aggregator Microservice na porta 5002")
    logger.info(f"Users Service URL: {USERS_SERVICE_URL}")
    app.run(host='0.0.0.0', port=5002, debug=False)