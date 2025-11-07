from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
import os
import redis
import structlog


load_dotenv()

LOG = structlog.get_logger()

SQLALCHEMY_DATABASE_URL = os.getenv("POSTGRES_URL")
REDIS_URL = os.getenv("REDIS_URL")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", 0))

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
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
        
        await redis_client.ping()
        LOG.info("Redis connection established")
        return redis_client
    except Exception as e:
        LOG.error(f"Redis connection failed: {e}")
        return None


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        LOG.info("Redis connection closed")