import redis
import json
import os
import logging

logger = logging.getLogger(__name__)

REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'cache-redis'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': 0,
    'decode_responses': True
}

def get_redis_client():
    try:
        client = redis.Redis(**REDIS_CONFIG)
        client.ping()
        return client
    except Exception as e:
        logger.error(f"Erro ao conectar ao Redis: {str(e)}")
        raise

def cache_get(key):
    try:
        client = get_redis_client()
        value = client.get(key)
        if value:
            logger.info(f"Cache GET - Key: {key} - FOUND")
            return json.loads(value)
        else:
            logger.info(f"Cache GET - Key: {key} - NOT FOUND")
            return None
    except Exception as e:
        logger.error(f"Erro ao ler cache: {str(e)}")
        return None

def cache_set(key, value, expiration=300):
    try:
        client = get_redis_client()
        serialized = json.dumps(value, default=str)
        result = client.setex(key, expiration, serialized)
        logger.info(f"Cache SET - Key: {key} - Expiration: {expiration}s - Success: {result}")
        return result
    except Exception as e:
        logger.error(f"Erro ao gravar cache: {str(e)}")
        return False

def cache_delete(key):
    try:
        client = get_redis_client()
        result = client.delete(key)
        logger.info(f"Cache DELETE - Key: {key} - Deleted: {result}")
        return result
    except Exception as e:
        logger.error(f"Erro ao deletar cache: {str(e)}")
        return False

def cache_clear():
    try:
        client = get_redis_client()
        result = client.flushdb()
        logger.info(f"Cache CLEAR - All keys deleted")
        return result
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {str(e)}")
        return False