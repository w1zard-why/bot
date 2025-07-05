# bot/app/main.py
import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.dispatcher.event.bases import SkipHandler
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
try:
    # старые версии (< 23.7)
    from aioprometheus import Counter, Service
except ImportError:
    # новые версии (>= 23.7) — Service лежит в под-модуле
    from aioprometheus import Counter
    from aioprometheus.service import Service

from app.config import get_settings
from app.cron.autobuyer import start_autobuyer
from app.db.queries import init_db
from app.handlers import admin, balance, core, gifts, payments, auto
from app.metrics import payments_total, purchases_total
from app.utils.logging import setup_logging

settings = get_settings()
setup_logging()

bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(core.router)
dp.include_router(balance.router)
dp.include_router(gifts.router)
dp.include_router(payments.router)
dp.include_router(admin.router)
dp.include_router(auto.router)


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.calls: defaultdict[int, list[datetime]] = defaultdict(list)

    async def __call__(self, handler, event, data):  # type: ignore[override]
        if not hasattr(event, "from_user"):
            return await handler(event, data)
        uid = event.from_user.id  # type: ignore[attr-defined]
        now = datetime.utcnow()
        window = timedelta(seconds=settings.RATE_LIMIT_WINDOW)
        self.calls[uid] = [t for t in self.calls[uid] if now - t < window]
        if len(self.calls[uid]) >= settings.RATE_LIMIT_CMDS:
            return
        self.calls[uid].append(now)
        return await handler(event, data)


dp.message.middleware(ThrottlingMiddleware())

metrics = Service()
counter = Counter("commands_total", "Total bot commands")

try:
    # старые релизы (< 23.7) — метод register у Service
    metrics.register(counter)
    metrics.register(payments_total)
    metrics.register(purchases_total)
except AttributeError:
    # новые релизы — регистрируем через registry, игнорируя повторную
    try:
        metrics.registry.register(counter)
        metrics.registry.register(payments_total)
        metrics.registry.register(purchases_total)
    except ValueError:
        # collector уже был добавлен — просто пропускаем
        pass


async def _on_startup() -> None:
    await init_db()
    start_autobuyer(bot)
    await metrics.start(addr="0.0.0.0", port=8001)


async def _polling() -> None:
    await _on_startup()
    await dp.start_polling(bot)


async def _webhook() -> None:
    from aiohttp import web

    app = web.Application()
    SimpleRequestHandler(dp, bot).register(app, path="/webhook")
    setup_application(app, dp, bot)
    await _on_startup()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    await bot.set_webhook(f"{settings.WEBHOOK_BASE}/webhook")
    logging.info("Webhook started")


if __name__ == "__main__":
    asyncio.run(_webhook() if settings.TG_MODE == "webhook" else _polling())