# bot/app/cron/autobuyer.py
import logging

import aiocron
from aiogram import Bot

from app.config import get_settings
from app.db import queries
from app.services.stars import spend_stars
from app.services.store_api import GiftStoreAPI
from app.metrics import purchases_total

settings = get_settings()
store = GiftStoreAPI()


def start_autobuyer(bot: Bot) -> None:
    """Запустить крон-таску, вызываемую в main.py."""

    @aiocron.crontab("*/1 * * * *")  # каждую минуту — внутри фильтруем по INTERVAL
    async def _task() -> None:  # noqa: WPS430
        try:
            await _run(bot)
        except Exception:  # pragma: no cover
            logging.exception("Autobuyer failed")


async def _run(bot: Bot) -> None:
    after_ts = await queries.last_gift_ts()
    gifts = await store.get_new_gifts(after_ts)
    if not gifts:
        return
    settings_map = await queries.load_gift_settings()

    for user in await queries.list_auto_users():
        uid = user["id"]
        for gift in gifts:
            cfg = settings_map.get(gift["id"])
            if not cfg:
                continue
            need_qty, max_price = cfg
            price = int(gift["price"])
            if price > max_price:
                continue
            have = await queries.user_have_gift(uid, gift["id"])
            if have >= need_qty:
                continue
            if await spend_stars(uid, price):
                await store.purchase(uid, gift["id"])
                await queries.record_purchase(uid, gift["id"], gift["name"], price)
                purchases_total.inc(price)
                await bot.send_message(uid, f"🎁 Куплен «{gift['name']}» за {price}⭐")
