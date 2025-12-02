from flask import Flask, jsonify, request
import logging
from datetime import datetime, timedelta
import random

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

orders_database = [
    {
        'id': 1001,
        'user_id': 1,
        'product': 'Notebook Dell',
        'quantity': 1,
        'total': 3500.00,
        'status': 'delivered',
        'created_at': (datetime.now() - timedelta(days=30)).isoformat()
    },
    {
        'id': 1002,
        'user_id': 2,
        'product': 'Mouse Logitech',
        'quantity': 2,
        'total': 171.00,
        'status': 'delivered',
        'created_at': (datetime.now() - timedelta(days=25)).isoformat()
    },
    {
        'id': 1003,
        'user_id': 1,
        'product': 'Teclado Mecânico',
        'quantity': 1,
        'total': 450.00,
        'status': 'shipped',
        'created_at': (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        'id': 1004,
        'user_id': 3,
        'product': 'Monitor LG 24"',
        'quantity': 2,
        'total': 1780.00,
        'status': 'processing',
        'created_at': (datetime.now() - timedelta(days=2)).isoformat()
    },
    {
        'id': 1005,
        'user_id': 2,
        'product': 'Webcam Full HD',
        'quantity': 1,
        'total': 320.00,
        'status': 'pending',
        'created_at': datetime.now().isoformat()
    }
]

@app.route('/orders', methods=['GET'])
def get_orders():
    logger.info(f"GET /orders - IP: {request.remote_addr}")
    
    user_id = request.args.get('user_id', type=int)
    status_filter = request.args.get('status')
    
    filtered_orders = orders_database.copy()
    
    if user_id:
        filtered_orders = [o for o in filtered_orders if o['user_id'] == user_id]
    
    if status_filter:
        filtered_orders = [o for o in filtered_orders if o['status'] == status_filter]
    
    total_value = sum(order['total'] for order in filtered_orders)
    
    return jsonify({
        'service': 'orders-service',
        'filters': {
            'user_id': user_id,
            'status': status_filter
        } if (user_id or status_filter) else None,
        'count': len(filtered_orders),
        'total_value': round(total_value, 2),
        'orders': filtered_orders
    }), 200

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    logger.info(f"GET /orders/{order_id} - IP: {request.remote_addr}")
    
    order = next((o for o in orders_database if o['id'] == order_id), None)
    
    if not order:
        return jsonify({
            'service': 'orders-service',
            'error': 'Order not found',
            'order_id': order_id
        }), 404
    
    return jsonify({
        'service': 'orders-service',
        'order': order
    }), 200

@app.route('/orders/stats', methods=['GET'])
def get_stats():
    logger.info(f"GET /orders/stats - IP: {request.remote_addr}")
    
    total_orders = len(orders_database)
    total_revenue = sum(order['total'] for order in orders_database)
    
    status_counts = {}
    for order in orders_database:
        status = order['status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    return jsonify({
        'service': 'orders-service',
        'total_orders': total_orders,
        'total_revenue': round(total_revenue, 2),
        'average_order_value': round(avg_order_value, 2),
        'orders_by_status': status_counts,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/orders/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'orders-service',
        'timestamp': datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    logger.info("Iniciando Orders Service na porta 5002")
    app.run(host='0.0.0.0', port=5002, debug=False)