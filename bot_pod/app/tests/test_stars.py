# tests/test_stars.py
import pytest

from app.db.queries import get_balance, init_db, register_user
from app.services.stars import add_stars, spend_stars


@pytest.mark.asyncio
async def test_add_and_spend():
    await init_db()
    uid = 1
    await register_user(uid, "tester")
    await add_stars(uid, 10)
    assert await get_balance(uid) == 10
    assert await spend_stars(uid, 5) is True
    assert await get_balance(uid) == 5
    assert await spend_stars(uid, 10) is False
