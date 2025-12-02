import psycopg2
from psycopg2.extras import RealDictCursor
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'banco-dados'),
    'database': os.getenv('DB_NAME', 'tasks_db'),
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'admin123'),
    'port': int(os.getenv('DB_PORT', 5432))
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def get_all_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY created_at DESC')
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    return tasks

def get_task_by_id(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = %s', (task_id,))
    task = cursor.fetchone()
    cursor.close()
    conn.close()
    return task

def create_task(title, description, status='pending'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s) RETURNING *',
        (title, description, status)
    )
    task = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return task

def update_task(task_id, title=None, description=None, status=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if title:
        updates.append('title = %s')
        params.append(title)
    if description:
        updates.append('description = %s')
        params.append(description)
    if status:
        updates.append('status = %s')
        params.append(status)
    
    updates.append('updated_at = CURRENT_TIMESTAMP')
    params.append(task_id)
    
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = %s RETURNING *"
    cursor.execute(query, params)
    task = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return task

def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = %s RETURNING *', (task_id,))
    task = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return task