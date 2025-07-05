# bot/app/handlers/gifts.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.db.queries import get_balance
from app.services.store_api import GiftStoreAPI

router = Router()
api = GiftStoreAPI()


@router.message(Command("gifts"))
async def cmd_gifts(msg: Message) -> None:
    gifts = await api.get_new_gifts(0)
    bal = await get_balance(msg.from_user.id)
    lines = [
        f"{g['id']}. {g['name']} — {g['price']} ⭐" + (" ✅" if bal >= g["price"] else "")
        for g in gifts
    ]
    await msg.answer("\n".join(lines))
