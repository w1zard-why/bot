from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.db import queries

router = Router()

@router.message(Command("autobuy_on"))
async def cmd_autobuy_on(msg: Message) -> None:
    await queries.set_auto_enabled(msg.from_user.id, True)
    await msg.answer("Автопокупки включены")

@router.message(Command("autobuy_off"))
async def cmd_autobuy_off(msg: Message) -> None:
    await queries.set_auto_enabled(msg.from_user.id, False)
    await msg.answer("Автопокупки отключены")
