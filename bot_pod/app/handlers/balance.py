# bot/app/handlers/balance.py
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.user_service import UserService

router = Router()

def _kb() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for n in (50, 100, 250, 500):
        kb.button(text=f"{n} ⭐", callback_data=f"topup_{n}")
    kb.button(text="Своя сумма", callback_data="topup_custom")
    return kb.as_markup()

@router.message(Command("balance"))
async def show_balance(msg: types.Message):
    stars = await UserService.get_stars(msg.from_user.id)
    await msg.answer(
        f"💰 Твой баланс: {stars} ⭐\n\nВыбери сумму пополнения:",
        reply_markup=_kb(),
    )
