# app/handlers/payments.py
import json
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import LabeledPrice
from app.services.user_service import UserService

router = Router()

class Ask(StatesGroup):
    waiting = State()

@router.callback_query(F.data == "topup_custom")
async def ask_amount(cb: types.CallbackQuery, state: FSMContext):
    await cb.message.answer("✏️ Введи число звёзд, которое хочешь купить:")
    await state.set_state(Ask.waiting)

@router.message(Ask.waiting, F.text.regexp(r"^\d+$"))
async def invoice_any(msg: types.Message, state: FSMContext):
    amount = int(msg.text)
    await state.clear()
    await msg.bot.send_invoice(
        msg.chat.id,
        title="Пополнение баланса",
        description=f"Пополнение баланса на {amount} ⭐",
        payload=json.dumps({"stars": amount}),
        currency="XTR",
        prices=[LabeledPrice(label="Звёзды", amount=amount)],
        provider_token=""
    )

@router.message(Ask.waiting)
async def wrong(msg: types.Message):
    await msg.answer("⚠️ Введи только цифры.")

# быстрые кнопки topup_50 / 100 / …
@router.callback_query(F.data.startswith("topup_"))
async def quick(cb: types.CallbackQuery):
    amount = int(cb.data.split("_")[1])
    await cb.bot.send_invoice(
        cb.from_user.id,
        title="Пополнение баланса",
        description=f"Пополнение баланса на {amount} ⭐",
        payload=json.dumps({"stars": amount}),
        currency="XTR",
        prices=[LabeledPrice(label="Звёзды", amount=amount)],
        provider_token=""
    )

# pre-checkout / success — оставляем как есть
@router.pre_checkout_query()
async def pre(pcq: types.PreCheckoutQuery):
    await pcq.bot.answer_pre_checkout_query(pcq.id, ok=True)

@router.message(F.successful_payment)
async def done(msg: types.Message):
    stars = json.loads(msg.successful_payment.invoice_payload)["stars"]
    await UserService.add_stars(msg.from_user.id, stars)
    await msg.answer(f"✅ Баланс пополнен на {stars} ⭐")
