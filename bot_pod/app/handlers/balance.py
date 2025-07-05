# bot/app/handlers/balance.py
import json
from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Message,
)

from app.config import get_settings
from app.db import queries
from app.db.queries import get_balance
from app.services.stars import add_stars

router = Router()
settings = get_settings()


@router.message(Command("balance"))
async def cmd_balance(msg: Message) -> None:
    bal = await get_balance(msg.from_user.id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пополнить 100⭐", callback_data="buy:100")],
            [InlineKeyboardButton(text="Пополнить 500⭐", callback_data="buy:500")],
            [InlineKeyboardButton(text="Пополнить 1000⭐", callback_data="buy:1000")],
        ]
    )
    await msg.answer(f"Баланс: {bal} ⭐", reply_markup=kb)


@router.callback_query(lambda c: c.data.startswith("buy:"))
async def on_buy(cb: CallbackQuery, bot: Bot) -> None:
    amount = int(cb.data.split(":", 1)[1])
    prices = [LabeledPrice(label=f"{amount} ⭐", amount=amount * 100)]
    await bot.send_invoice(
        chat_id=cb.from_user.id,
        title=f"{amount} ⭐",
        payload=json.dumps({"stars": amount}),
        provider_token=settings.PAYMENT_PROVIDER_TOKEN or "",
        currency="RUB",
        prices=prices,
    )
    await cb.answer()


@router.message(Command("buy"))
async def cmd_buy(msg: Message, bot: Bot) -> None:
    parts = msg.text.split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        return await msg.answer("Использование: /buy <N>")
    amount = int(parts[1])
    prices = [LabeledPrice(label=f"{amount} ⭐", amount=amount * 100)]
    await bot.send_invoice(
        chat_id=msg.from_user.id,
        title=f"{amount} ⭐",
        payload=json.dumps({"stars": amount}),
        provider_token=settings.PAYMENT_PROVIDER_TOKEN or "",
        currency="RUB",
        prices=prices,
    )


@router.message(Command("topup"))
async def cmd_topup(msg: Message) -> None:
    parts = msg.text.split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        return await msg.answer("Использование: /topup <N>")
    n = int(parts[1])
    await add_stars(msg.from_user.id, n)
    await msg.answer(f"Пополнено на {n} ⭐")