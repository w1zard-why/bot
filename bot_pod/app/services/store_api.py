from typing import Any, Dict, List, Optional

from aiohttp import ClientSession
from app.config import get_settings

class GiftStoreAPI:
    """
    Мини-клиент подарочного магазина.
    Сессию создаём лениво при первом запросе, чтобы не требовался
    уже запущенный event-loop во время импорта модуля.
    """

    def __init__(self, base_url: str | None = None) -> None:
        # если аргумент не передан, берём URL из .env
        self._base = base_url or get_settings().GIFT_API_BASE
        self._session: Optional[ClientSession] = None

    async def _get_session(self) -> ClientSession:
        if self._session is None or self._session.closed:
            self._session = ClientSession()
        return self._session

    async def get_new_gifts(self, after_ts: int) -> List[Dict[str, Any]]:
        session = await self._get_session()
        async with session.get(f"{self._base}/gifts", params={"after": after_ts}) as r:
            r.raise_for_status()
            return await r.json()

    async def purchase(self, user_id: int, gift_id: str) -> None:
        session = await self._get_session()
        async with session.post(
            f"{self._base}/purchase", json={"user_id": user_id, "gift_id": gift_id}
        ) as r:
            r.raise_for_status()

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
