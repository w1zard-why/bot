from aiogram import Router, types
from aiogram.filters import Command
from app.services.user_service import UserService

router = Router()

@router.message(Command("autobuy_on"))
async def autobuy_on(msg: types.Message):
    await UserService.set_autobuy(msg.from_user.id, True)
    await msg.answer("✅ Автопокупка включена.")

@router.message(Command("autobuy_off"))
async def autobuy_off(msg: types.Message):
    await UserService.set_autobuy(msg.from_user.id, False)
    await msg.answer("❌ Автопокупка отключена.")

@router.message(Command("autobuy_set"))
async def autobuy_set(msg: types.Message):
    try:
        _, max_price, max_qty = msg.text.split()
        await UserService.set_autobuy_settings(
            msg.from_user.id, int(max_price), int(max_qty)
        )
        await msg.answer(
            f"✅ Лимит цены: {max_price} ⭐, кол-во: {max_qty}"
        )
    except ValueError:
        await msg.answer("⚠️ Формат: /autobuy_set <макс-цена> <макс-кол-во>")
