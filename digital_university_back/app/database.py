from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
import os
import redis
import structlog
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

load_dotenv()

LOG = structlog.get_logger()

SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URL")
REDIS_URL = os.getenv("REDIS_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", 0))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")

def setup_database():
    """Создает БД если она не существует"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        if not cursor.fetchone():
            cursor.execute(f'CREATE DATABASE "{DB_NAME}"')
            LOG.info(f" База данных {DB_NAME} создана")
        cursor.close()
        conn.close()
        
    except Exception as e:
        LOG.error(f"Ошибка при создании БД: {e}")
        raise

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,  # строка url postgresql+asyncpg ... 
    echo=True,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


Base = declarative_base()
redis_client = None

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_engine():
    await engine.dispose()


async def get_redis() -> redis.Redis:
    return redis_client


async def init_redis():
    global redis_client
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD"),
            db=REDIS_DB,
            decode_responses=True, 
            encoding="utf-8",
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        redis_client.ping()
        LOG.info("Redis connection established")
        return redis_client
    except Exception as e:
        LOG.error(f"Redis connection failed: {e}")
        return None


async def close_redis():
    global redis_client
    if redis_client:
        redis_client.close()
        LOG.info("Redis connection closed")