import asyncpg

from src import settings
from contextlib import asynccontextmanager


db = {"data": b"foobar"}



async def setup_pool():
    settings.POSTGRESS_POOL = await asyncpg.create_pool(settings.POSTGRES_DSN)


async def get_connection():
    async with settings.POSTGRESS_POOL.acquire() as connection:
        async with connection.transaction():
            yield connection

async def setup_tables():
    async with get_connection() as conn:
        await conn.execute('''
            CREATE TABLE messages(
                id VARCHAR(22),
                created timestamp,
                data VARCHAR(15000)
            )
        ''')


async def create(id, data):
    db[id] = data.decode("ascii")
    return None


async def get_latest(id):
    return db[id]


async def get_stream(id):
    for i in range(20):
        yield db[id]
