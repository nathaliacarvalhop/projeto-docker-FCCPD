import logging
import sys
from datetime import datetime
from models import get_engine, get_session, init_database, Usuario, Produto

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def populate_database():
    try:
        logger.info("Iniciando conexao com banco de dados SQLite...")
        engine = get_engine()
        
        logger.info("Criando tabelas no banco de dados...")
        init_database(engine)
        
        session = get_session(engine)
        
        usuarios_data = [
            ('Joao Silva', 'joao.silva@email.com'),
            ('Maria Santos', 'maria.santos@email.com'),
            ('Pedro Oliveira', 'pedro.oliveira@email.com'),
            ('Ana Costa', 'ana.costa@email.com'),
            ('Carlos Souza', 'carlos.souza@email.com')
        ]
        
        logger.info("Inserindo usuarios no banco de dados...")
        usuarios_inseridos = 0
        for nome, email in usuarios_data:
            existing = session.query(Usuario).filter_by(email=email).first()
            if not existing:
                usuario = Usuario(nome=nome, email=email)
                session.add(usuario)
                usuarios_inseridos += 1
        
        produtos_data = [
            ('Notebook Dell', 3500.00, 10),
            ('Mouse Logitech', 85.50, 50),
            ('Teclado Mecanico', 450.00, 25),
            ('Monitor LG 24"', 890.00, 15),
            ('Webcam Full HD', 320.00, 30)
        ]
        
        logger.info("Inserindo produtos no banco de dados...")
        produtos_inseridos = 0
        for nome, preco, estoque in produtos_data:
            produto = Produto(nome=nome, preco=preco, estoque=estoque)
            session.add(produto)
            produtos_inseridos += 1
        
        session.commit()
        
        total_usuarios = session.query(Usuario).count()
        total_produtos = session.query(Produto).count()
        
        logger.info("=" * 70)
        logger.info("DADOS INSERIDOS COM SUCESSO!")
        logger.info(f"Usuarios inseridos nesta execucao: {usuarios_inseridos}")
        logger.info(f"Produtos inseridos nesta execucao: {produtos_inseridos}")
        logger.info(f"Total de usuarios no banco: {total_usuarios}")
        logger.info(f"Total de produtos no banco: {total_produtos}")
        logger.info(f"Timestamp da insercao: {datetime.now().isoformat()}")
        logger.info(f"Arquivo do banco: /data/desafio2.db")
        logger.info("=" * 70)
        
        session.close()
        
    except Exception as e:
        logger.error(f"Erro ao popular banco de dados: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    populate_database()