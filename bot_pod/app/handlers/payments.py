# bot/app/handlers/payments.py
import json
from aiogram import Router, Bot
from aiogram.types import Message, PreCheckoutQuery

from app.db import queries
from app.services.stars import add_stars
from app.metrics import payments_total

router = Router()


@router.pre_checkout_query()
async def on_pre_checkout(q: PreCheckoutQuery, bot: Bot) -> None:
    await bot.answer_pre_checkout_query(q.id, ok=True)


@router.message()
async def on_successful_payment(msg: Message) -> None:
    if msg.successful_payment:
        stars = int(json.loads(msg.successful_payment.invoice_payload)["stars"])
        charge_id = msg.successful_payment.provider_payment_charge_id
        if await queries.record_payment(charge_id, msg.from_user.id, stars):
            await add_stars(msg.from_user.id, stars)
            payments_total.inc(stars)
            await msg.answer(f"Баланс пополнен на {stars} ⭐")
