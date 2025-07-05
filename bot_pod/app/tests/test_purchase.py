# tests/test_purchase.py
# Небольшой smoke-тест spend/add в транзакции.
import pytest

from app.db.queries import init_db, register_user
from app.services.stars import add_stars, spend_stars


@pytest.mark.asyncio
async def test_tx_atomicity():
    await init_db()
    uid = 7
    await register_user(uid, "atomic")
    await add_stars(uid, 1)
    assert await spend_stars(uid, 1) is True
    assert await spend_stars(uid, 1) is False
