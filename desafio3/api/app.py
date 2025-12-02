from flask import Flask, jsonify, request
import logging
import time
import models
import cache
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def serialize_task(task):
    if not task:
        return None
    
    task_dict = dict(task)
    
    if 'created_at' in task_dict and task_dict['created_at']:
        task_dict['created_at'] = task_dict['created_at'].isoformat()
    if 'updated_at' in task_dict and task_dict['updated_at']:
        task_dict['updated_at'] = task_dict['updated_at'].isoformat()
    
    return task_dict

@app.before_request
def log_request():
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'Tasks API',
        'version': '1.0',
        'endpoints': {
            'tasks': '/tasks',
            'task_by_id': '/tasks/<id>',
            'create_task': 'POST /tasks',
            'update_task': 'PUT /tasks/<id>',
            'delete_task': 'DELETE /tasks/<id>',
            'health': '/health',
            'cache_stats': '/cache/stats'
        }
    }), 200

@app.route('/health', methods=['GET'])
def health():
    try:
        conn = models.get_db_connection()
        conn.close()
        db_status = 'healthy'
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = 'unhealthy'
    
    try:
        redis_client = cache.get_redis_client()
        redis_client.ping()
        cache_status = 'healthy'
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        cache_status = 'unhealthy'
    
    return jsonify({
        'api': 'healthy',
        'database': db_status,
        'cache': cache_status
    }), 200

@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        cache_key = 'all_tasks'
        
        cached_data = cache.cache_get(cache_key)
        if cached_data:
            logger.info("Cache HIT - Retornando dados do Redis")
            return jsonify({
                'source': 'cache',
                'count': len(cached_data),
                'tasks': cached_data
            }), 200
        
        logger.info("Cache MISS - Consultando banco de dados")
        tasks = models.get_all_tasks()
        tasks_list = [serialize_task(task) for task in tasks]
        
        cache.cache_set(cache_key, tasks_list, expiration=60)
        
        return jsonify({
            'source': 'database',
            'count': len(tasks_list),
            'tasks': tasks_list
        }), 200
    
    except Exception as e:
        logger.error(f"Error in get_tasks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        cache_key = f'task_{task_id}'
        
        cached_data = cache.cache_get(cache_key)
        if cached_data:
            logger.info(f"Cache HIT - Task {task_id}")
            return jsonify({
                'source': 'cache',
                'task': cached_data
            }), 200
        
        logger.info(f"Cache MISS - Task {task_id}")
        task = models.get_task_by_id(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        task_dict = serialize_task(task)
        cache.cache_set(cache_key, task_dict, expiration=60)
        
        return jsonify({
            'source': 'database',
            'task': task_dict
        }), 200
    
    except Exception as e:
        logger.error(f"Error in get_task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        
        if not data or 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        task = models.create_task(
            title=data['title'],
            description=data.get('description', ''),
            status=data.get('status', 'pending')
        )
        
        cache.cache_delete('all_tasks')
        
        logger.info(f"Nova task criada: {task['id']}")
        
        return jsonify({
            'message': 'Task created successfully',
            'task': serialize_task(task)
        }), 201
    
    except Exception as e:
        logger.error(f"Error in create_task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        data = request.get_json()
        
        task = models.update_task(
            task_id,
            title=data.get('title'),
            description=data.get('description'),
            status=data.get('status')
        )
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        cache.cache_delete('all_tasks')
        cache.cache_delete(f'task_{task_id}')
        
        logger.info(f"Task atualizada: {task_id}")
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': serialize_task(task)
        }), 200
    
    except Exception as e:
        logger.error(f"Error in update_task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task = models.delete_task(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        cache.cache_delete('all_tasks')
        cache.cache_delete(f'task_{task_id}')
        
        logger.info(f"Task deletada: {task_id}")
        
        return jsonify({
            'message': 'Task deleted successfully',
            'task': serialize_task(task)
        }), 200
    
    except Exception as e:
        logger.error(f"Error in delete_task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/cache/stats', methods=['GET'])
def cache_stats():
    try:
        redis_client = cache.get_redis_client()
        info = redis_client.info()
        
        return jsonify({
            'connected_clients': info['connected_clients'],
            'used_memory_human': info['used_memory_human'],
            'total_commands_processed': info['total_commands_processed'],
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0)
        }), 200
    except Exception as e:
        logger.error(f"Error in cache_stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    try:
        cache.cache_clear()
        logger.info("Cache limpo manualmente")
        return jsonify({'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        logger.error(f"Error in clear_cache: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Iniciando API na porta 5000")
    app.run(host='0.0.0.0', port=5000, debug=False)