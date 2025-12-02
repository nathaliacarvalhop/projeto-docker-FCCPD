CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tasks_status ON tasks(status);

INSERT INTO tasks (title, description, status) VALUES
    ('Estudar para a prova', 'estudar microserviços e docker', 'in_progress'),
    ('Fazer as marmitas', 'Fazer almoço pra semana', 'completed'),
    ('Terminar projeto', 'terminar projeto', 'pending');