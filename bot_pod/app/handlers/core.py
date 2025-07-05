# bot/app/handlers/core.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import get_settings
from app.db.queries import register_user
from app.services.stars import add_stars

router = Router()
settings = get_settings()


@router.message(Command("start"))
async def cmd_start(msg: Message) -> None:
    await register_user(msg.from_user.id, msg.from_user.username or "")
    if settings.INITIAL_STARS:
        await add_stars(msg.from_user.id, settings.INITIAL_STARS)
        await msg.answer(
            f"Добро пожаловать! Начислено {settings.INITIAL_STARS} ⭐"
        )
    else:
        await msg.answer("Добро пожаловать!")