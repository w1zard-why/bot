# bot/app/handlers/admin.py
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.config import get_settings
from app.db import queries

router = Router()
settings = get_settings()


def is_admin(user_id: int) -> bool:
    return str(user_id) in settings.ADMINS.split(",") if settings.ADMINS else False


@router.message(Command("gift_set"))
async def cmd_gift_set(msg: Message) -> None:
    if not is_admin(msg.from_user.id):
        return
    parts = msg.text.split()
    if len(parts) != 4 or not parts[2].isdigit() or not parts[3].isdigit():
        return await msg.answer("Использование: /gift_set <gift_id> <qty> <price>")
    await queries.upsert_gift_setting(parts[1], int(parts[2]), int(parts[3]))
    await msg.answer("OK")


@router.message(Command("gift_del"))
async def cmd_gift_del(msg: Message) -> None:
    if not is_admin(msg.from_user.id):
        return
    parts = msg.text.split()
    if len(parts) != 2:
        return await msg.answer("Использование: /gift_del <gift_id>")
    await queries.delete_gift_setting(parts[1])
    await msg.answer("OK")


@router.message(Command("gift_list"))
async def cmd_gift_list(msg: Message) -> None:
    if not is_admin(msg.from_user.id):
        return
    rows = await queries.list_gift_settings()
    if not rows:
        await msg.answer("Empty")
    else:
        lines = [
            f"{r['gift_id']} qty={r['target_qty']} price={r['max_price']}" for r in rows
        ]
        await msg.answer("\n".join(lines))
