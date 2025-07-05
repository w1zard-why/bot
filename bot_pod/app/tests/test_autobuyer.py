# tests/test_autobuyer.py
from unittest.mock import AsyncMock

import pytest

from app.cron.autobuyer import _run
from app.db.queries import add_stars, init_db, register_user
from app.services import store_api


@pytest.mark.asyncio
async def test_autobuyer(monkeypatch):
    await init_db()
    uid = 42
    await register_user(uid, "auto")
    await add_stars(uid, 100)

    fake_store = AsyncMock()
    fake_store.get_new_gifts.return_value = [{"id": "g1", "name": "Rose", "price": 5}]
    fake_store.purchase.return_value = None
    monkeypatch.setattr(store_api, "GiftStoreAPI", lambda: fake_store)

    bot = AsyncMock()
    await _run(bot)
    fake_store.purchase.assert_called_once()
