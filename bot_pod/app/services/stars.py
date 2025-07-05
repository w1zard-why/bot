# bot/app/services/stars.py
import asyncpg

from app.db.queries import pool


async def add_stars(user_id: int, amount: int) -> None:
    async with (await pool()).acquire() as conn, conn.transaction():
        bal = await conn.fetchval("SELECT stars FROM balances WHERE user_id=$1 FOR UPDATE", user_id)
        if bal is None:
            await conn.execute("INSERT INTO balances(user_id, stars) VALUES($1,$2)", user_id, amount)
        else:
            await conn.execute("UPDATE balances SET stars=stars+$2 WHERE user_id=$1", user_id, amount)


async def spend_stars(user_id: int, amount: int) -> bool:
    async with (await pool()).acquire() as conn, conn.transaction():
        bal = await conn.fetchval("SELECT stars FROM balances WHERE user_id=$1 FOR UPDATE", user_id)
        if bal is None or bal < amount:
            return False
        await conn.execute("UPDATE balances SET stars=stars-$2 WHERE user_id=$1", user_id, amount)
        return True
