from pathlib import Path
from typing import Any, List, Optional

import asyncpg

from app.config import get_settings

_SQL = Path(__file__).with_suffix(".sql").read_text()
_pool: Optional[asyncpg.Pool] = None


async def pool() -> asyncpg.Pool:
    """
    Возвращает singleton-пул соединений.
    Приводим PG_DSN к str, потому что в Pydantic v2 это объект,
    а asyncpg ожидает строковый DSN.
    """
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            dsn=str(get_settings().PG_DSN),  # ← фикс
            min_size=1,
            max_size=5,
        )
    return _pool


async def init_db() -> None:
    async with (await pool()).acquire() as conn:
        await conn.execute(_SQL)


async def register_user(user_id: int, username: str) -> None:
    q = (
        "INSERT INTO users(id, username) VALUES($1,$2) "
        "ON CONFLICT(id) DO UPDATE SET username = EXCLUDED.username"
    )
    async with (await pool()).acquire() as conn:
        await conn.execute(q, user_id, username)


async def get_balance(user_id: int) -> int:
    async with (await pool()).acquire() as conn:
        bal: Optional[int] = await conn.fetchval(
            "SELECT stars FROM balances WHERE user_id=$1",
            user_id,
        )
        return bal or 0


async def list_auto_users() -> List[asyncpg.Record]:
    q = "SELECT id FROM users WHERE auto_enabled"
    async with (await pool()).acquire() as conn:
        return await conn.fetch(q)


async def set_auto_enabled(user_id: int, enabled: bool) -> None:
    q = "UPDATE users SET auto_enabled=$2 WHERE id=$1"
    async with (await pool()).acquire() as conn:
        await conn.execute(q, user_id, enabled)


async def last_gift_ts() -> int:
    q = "SELECT COALESCE(MAX(purchased_at),0)::BIGINT FROM purchases"
    async with (await pool()).acquire() as conn:
        return await conn.fetchval(q)


async def record_purchase(
    user_id: int,
    gift_id: str,
    gift_name: str,
    spent: int,
) -> None:
    q = (
        "INSERT INTO purchases(user_id,gift_id,gift_name,spent) "
        "VALUES($1,$2,$3,$4)"
    )
    async with (await pool()).acquire() as conn:
        await conn.execute(q, user_id, gift_id, gift_name, spent)


async def add_stars(user_id: int, amount: int) -> None:
    async with (await pool()).acquire() as conn, conn.transaction():
        bal = await conn.fetchval(
            "SELECT stars FROM balances WHERE user_id=$1 FOR UPDATE", user_id
        )
        if bal is None:
            await conn.execute(
                "INSERT INTO balances(user_id, stars) VALUES($1,$2)", user_id, amount
            )
        else:
            await conn.execute(
                "UPDATE balances SET stars=stars+$2 WHERE user_id=$1", user_id, amount
            )


async def spend_stars(user_id: int, amount: int) -> bool:
    async with (await pool()).acquire() as conn, conn.transaction():
        bal = await conn.fetchval(
            "SELECT stars FROM balances WHERE user_id=$1 FOR UPDATE", user_id
        )
        if bal is None or bal < amount:
            return False
        await conn.execute(
            "UPDATE balances SET stars=stars-$2 WHERE user_id=$1", user_id, amount
        )
        return True


async def record_payment(invoice_id: str, user_id: int, stars: int) -> bool:
    q = (
        "INSERT INTO payments(invoice_id,user_id,stars) VALUES($1,$2,$3) "
        "ON CONFLICT(invoice_id) DO NOTHING RETURNING 1"
    )
    async with (await pool()).acquire() as conn:
        return bool(await conn.fetchval(q, invoice_id, user_id, stars))


async def upsert_gift_setting(gift_id: str, qty: int, price: int) -> None:
    q = (
        "INSERT INTO gifts_settings(gift_id,target_qty,max_price) "
        "VALUES($1,$2,$3) "
        "ON CONFLICT(gift_id) DO UPDATE SET "
        "target_qty=EXCLUDED.target_qty, max_price=EXCLUDED.max_price"
    )
    async with (await pool()).acquire() as conn:
        await conn.execute(q, gift_id, qty, price)


async def delete_gift_setting(gift_id: str) -> None:
    async with (await pool()).acquire() as conn:
        await conn.execute("DELETE FROM gifts_settings WHERE gift_id=$1", gift_id)


async def list_gift_settings() -> List[asyncpg.Record]:
    async with (await pool()).acquire() as conn:
        return await conn.fetch(
            "SELECT gift_id,target_qty,max_price FROM gifts_settings ORDER BY gift_id"
        )


async def load_gift_settings() -> dict[str, tuple[int, int]]:
    rows = await list_gift_settings()
    return {r["gift_id"]: (r["target_qty"], r["max_price"]) for r in rows}


async def user_have_gift(user_id: int, gift_id: str) -> int:
    async with (await pool()).acquire() as conn:
        return await conn.fetchval(
            "SELECT COUNT(*) FROM purchases WHERE user_id=$1 AND gift_id=$2",
            user_id,
            gift_id,
        )