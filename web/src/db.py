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
            create type operation_type as enum('write', 'read');
        ''')
        await conn.execute('''
            CREATE TABLE messages
            (
                created_at TIMESTAMP DEFAULT NOW(),
                hash_id varchar(22),
                data text,
                PRIMARY KEY (hash_id, created_at)
            )
        ''')
        await conn.execute('''
            CREATE FUNCTION delete_old_messages() RETURNS trigger
                LANGUAGE plpgsql
                AS $$
            BEGIN
                DELETE FROM messages WHERE created_at < NOW() - INTERVAL '1 days';
                RETURN NULL;
            END;
            $$;
        ''')
        await conn.execute('''
            CREATE TRIGGER trigger_delete_old_messages
            AFTER INSERT ON messages
            EXECUTE PROCEDURE delete_old_messages();
        ''')
        await conn.execute('''
            CREATE TABLE message_statistics 
            (
                created_at TIMESTAMP DEFAULT NOW(),
                hash_id varchar(22),
                operation operation_type,
                data_length int,
                location json,
                PRIMARY KEY (hash_id, created_at)
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
