from dotenv import load_dotenv
load_dotenv()
import os
import logging
from telethon import TelegramClient, functions, types

# Сначала проверяем, что .env подхватил нужные переменные
API_ID_ENV = os.getenv("TG_API_ID")
API_HASH  = os.getenv("TG_API_HASH")
if not (API_ID_ENV and API_HASH):
    raise RuntimeError("Ошибка: переменные TG_API_ID и TG_API_HASH должны быть заданы в .env")

API_ID   = int(API_ID_ENV)
SESSION  = os.getenv("TG_SESSION", "gifts")
PHONE    = os.getenv("TG_PHONE")  # нужен только при первом запуске

class MTGiftClient:
    def __init__(self):
        self._cli = TelegramClient(SESSION, API_ID, API_HASH)

    async def start(self):
        await self._cli.connect()
        if not await self._cli.is_user_authorized():
            await self._cli.send_code_request(PHONE)
            code = input("Введите код из Telegram: ")
            await self._cli.sign_in(PHONE, code)

    async def list_gifts(self) -> list[types.StarGift]:
        res = await self._cli(functions.payments.GetStarGiftsRequest(hash=0))
        return [g for g in res.gifts if not g.sold_out]

    async def buy_and_send(self, gift: types.StarGift, to_uid: int):
        inv = types.InputInvoiceStarGift(
            user_id=await self._cli.get_input_entity(to_uid),
            gift_id=gift.id,
            hide_name=False
        )
        pf = await self._cli(
            functions.payments.GetPaymentFormRequest(
                invoice=inv,
                theme_params=types.DataJSON(data="{}")
            )
        )
        await self._cli(
            functions.payments.SendPaymentFormRequest(
                form_id       = pf.form_id,
                invoice       = inv,
                payment_token = pf.payment_token
            )
        )
        logging.info(f"🎁 Куплен {gift.slug} за {gift.stars}⭐ → user {to_uid}")

_client: MTGiftClient | None = None

def client() -> MTGiftClient:
    global _client
    if _client is None:
        _client = MTGiftClient()
    return _client
