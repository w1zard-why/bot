# tests/test_registration.py
import pytest

from app.db.queries import get_balance, init_db, register_user


@pytest.mark.asyncio
async def test_registration():
    await init_db()
    uid = 99
    await register_user(uid, "newbie")
    assert await get_balance(uid) == 0
