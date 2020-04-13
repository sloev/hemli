import asyncio

import asyncpg

from fastapi import HTTPException


from src import settings
from contextlib import asynccontextmanager


async def setup_pool():
    settings.POSTGRESS_POOL = await asyncpg.create_pool(settings.POSTGRES_DSN)


async def get_connection():
    async with settings.POSTGRESS_POOL.acquire() as connection:
        async with connection.transaction():
            yield connection


async def setup_tables():
    async with get_connection() as conn:
        await conn.execute(
            """
            create type operation_type as enum('write', 'read');
        """
        )
        await conn.execute(
            """
            CREATE TABLE messages
            (
                created_at TIMESTAMP DEFAULT NOW(),
                hash_id varchar(22),
                data text,
                PRIMARY KEY (hash_id, created_at)
            )
        """
        )
        await conn.execute(
            """
            CREATE FUNCTION delete_old_messages() RETURNS trigger
                LANGUAGE plpgsql
                AS $$
            BEGIN
                DELETE FROM messages WHERE created_at < NOW() - INTERVAL '1 days';
                RETURN NULL;
            END;
            $$;
        """
        )
        await conn.execute(
            """
            CREATE TRIGGER trigger_delete_old_messages
            AFTER INSERT ON messages
            EXECUTE PROCEDURE delete_old_messages();
        """
        )
        await conn.execute(
            """
            CREATE TABLE message_statistics 
            (
                created_at TIMESTAMP,
                hash_id varchar(22),
                operation operation_type,
                data_length int,
                location json,
                PRIMARY KEY (hash_id, created_at)
            )
        """
        )
        await conn.execute(
            """
            CREATE FUNCTION delete_old_messages_statistics() RETURNS trigger
                LANGUAGE plpgsql
                AS $$
            BEGIN
                DELETE FROM message_statistics WHERE created_at < NOW() - INTERVAL '90 days';
                RETURN NULL;
            END;
            $$;
        """
        )
        await conn.execute(
            """
            CREATE TRIGGER trigger_delete_old_messages_statistics
            AFTER INSERT ON message_statistics
            EXECUTE PROCEDURE delete_old_messages_statistics();
        """
        )


async def log_message_statistics(created_at, hash_id, operation, data_length, location):
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO message_statistics(created_at, hash_id, operation, data_length, location)
            VALUES ($1, $2, $3, $4, $5)
        """,
            created_at,
            hash_id,
            operation,
            data_length,
            location,
        )


async def create(hash_id, base64_string):
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO messages (hash_id, data)
            VALUES ($1, $2)
        """,
            hash_id,
            base64_string,
        )


async def get_latest(hash_id):
    async with get_connection() as conn:
        result = await conn.fetchrow(
            """
            SELECT created_at, hash_id, data from messages 
            where hash_id = $1 
            order by created_at desc 
            limit 1
        """,
            hash_id,
        )
        if result:
            return dict(result)
        else:
            raise HTTPException(status_code=404, detail="no data for given hash_id")


async def get_stream(hash_id, from_datetime):
    while True:
        async with get_connection() as conn:
            result = await conn.fetchrow(
                """
                SELECT created_at, hash_id, data from messages 
                where hash_id = $1 
                and created_at > $2
                order by created_at desc 
                limit 1
            """,
                hash_id,
                from_datetime,
            )
        if result:
            yield dict(result)
        await asyncio.sleep(1)
