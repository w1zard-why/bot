import logging
from telethon import types, functions
from app.services.gift_mtproto import client
from app.services.user_service import UserService


class GiftService:
    @staticmethod
    async def list_regular():
        cli = client()
        await cli.start()
        gifts = await cli.list_gifts()
        return [
            dict(id=g.id, price=g.stars, emoji=g.emoji)
            for g in gifts
        ]

    @staticmethod
    async def buy(user_id: int, gift_id: int, price: int) -> bool:
        cli = client()
        await cli.start()

        # проверяем баланс
        if not await UserService.try_spend(user_id, price):
            return False

        try:
            # сама покупка без всяких оплат — Telegram сразу списывает звёзды
            await cli(functions.messages.SendStarGiftRequest(
                user_id=user_id,
                gift_id=gift_id
            ))
            logging.info("Gift %s bought for uid=%s", gift_id, user_id)
            return True
        except Exception as e:
            # если не вышло — возвращаем звёзды
            logging.error("Gift buy failed: %s", e)
            await UserService.add_stars(user_id, price)
            return False
