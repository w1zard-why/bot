# app/handlers/topup_custom.py
import json
from aiogram import Router, F, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import LabeledPrice

router = Router()

class Topup(StatesGroup):
    wait_amount = State()

@router.message(F.text == "💳 Пополнить баланс")
async def ask_amount(msg: types.Message, state: FSMContext):
    await msg.answer("✏️ Введи количество звёзд для покупки:")
    await state.set_state(Topup.wait_amount)

@router.message(Topup.wait_amount, F.text.regexp(r"^\d+$"))
async def send_invoice(msg: types.Message, state: FSMContext):
    amount = int(msg.text)
    await state.clear()

    await msg.bot.send_invoice(
        chat_id=msg.chat.id,
        title="Пополнение баланса",
        description=f"Пополнение баланса на {amount} ⭐",
        payload=json.dumps({"stars": amount}),
        currency="XTR",
        prices=[LabeledPrice(label="Звёзды", amount=amount * 100)],
        provider_token=""
    )

@router.message(Topup.wait_amount)
async def invalid(msg: types.Message):
    await msg.answer("⚠️ Введи сумму цифрами (например 150).")
