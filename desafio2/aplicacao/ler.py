import logging
import sys
from models import get_engine, get_session, Usuario, Produto

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def read_database():
    try:
        logger.info("Conectando ao banco de dados SQLite...")
        engine = get_engine()
        session = get_session(engine)
        
        logger.info("=" * 70)
        logger.info("LEITURA DE DADOS PERSISTIDOS NO VOLUME")
        logger.info("=" * 70)
        
        usuarios = session.query(Usuario).order_by(Usuario.id).all()
        
        logger.info(f"\n>>> USUARIOS CADASTRADOS ({len(usuarios)} registros):")
        if len(usuarios) == 0:
            logger.warning("  Nenhum usuario encontrado no banco!")
        else:
            for user in usuarios:
                logger.info(f"  [ID: {user.id}] {user.nome} - {user.email} (Criado: {user.data_criacao})")
        
        produtos = session.query(Produto).order_by(Produto.id).all()
        
        logger.info(f"\n>>> PRODUTOS CADASTRADOS ({len(produtos)} registros):")
        if len(produtos) == 0:
            logger.warning("  Nenhum produto encontrado no banco!")
        else:
            for produto in produtos:
                logger.info(f"  [ID: {produto.id}] {produto.nome} - R$ {produto.preco:.2f} | Estoque: {produto.estoque} (Criado: {produto.data_criacao})")
        
        logger.info("\n" + "=" * 70)
        if len(usuarios) > 0 or len(produtos) > 0:
            logger.info("COMPROVACAO: Dados foram recuperados do volume persistente!")
        else:
            logger.info("Banco de dados vazio. Execute o script de populacao primeiro.")
        logger.info("=" * 70)
        
        session.close()
        
    except Exception as e:
        logger.error(f"Erro ao ler dados: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    read_database()