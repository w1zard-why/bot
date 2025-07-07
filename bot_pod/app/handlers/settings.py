from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.services.user_service import UserService
from app.services.gift_service import GiftService
import re

router = Router()

def _kb(d):
    k = InlineKeyboardBuilder()
    k.button(text=f"Автопокупка {'✅' if d['autobuy'] else '❌'}", callback_data="toggle")
    k.button(text=f"Макс. цена: {d['max_price']}⭐", callback_data="price")
    k.button(text=f"Макс. кол-во: {d['max_qty']}", callback_data="qty")
    k.button(text="Купить обычный подарок", callback_data="buy_regular")
    k.adjust(1)
    return k.as_markup()

async def _show(chat_id, bot, d):
    txt = (
        "⚙️ <b>Настройки автопокупки</b>\n"
        f"• Статус: {'вкл' if d['autobuy'] else 'выкл'}\n"
        f"• Макс. цена: {d['max_price']} ⭐\n"
        f"• Макс. кол-во: {d['max_qty']}"
    )
    await bot.send_message(chat_id, txt, parse_mode="HTML", reply_markup=_kb(d))

@router.message(F.text == "⚙️ Настройки")
async def open_menu(msg: types.Message):
    d = await UserService.get_settings(msg.from_user.id)
    await _show(msg.chat.id, msg.bot, d)

@router.callback_query(F.data == "toggle")
async def toggle(cb: types.CallbackQuery):
    d = await UserService.toggle_autobuy(cb.from_user.id)
    await cb.message.edit_reply_markup(reply_markup=_kb(d))

@router.callback_query(F.data == "price")
async def ask_price(cb: types.CallbackQuery, state):
    await cb.message.edit_text("Введите новую максимальную цену в ⭐:")
    await state.set_state("wait_price")

@router.message(F.state == "wait_price", F.text.regexp(r"^\d+$"))
async def set_price(msg: types.Message, state):
    d = await UserService.set_price(msg.from_user.id, int(msg.text))
    await _show(msg.chat.id, msg.bot, d)
    await state.clear()

@router.callback_query(F.data == "qty")
async def ask_qty(cb: types.CallbackQuery, state):
    await cb.message.edit_text("Введите новое максимальное кол-во:")
    await state.set_state("wait_qty")

@router.message(F.state == "wait_qty", F.text.regexp(r"^\d+$"))
async def set_qty(msg: types.Message, state):
    d = await UserService.set_qty(msg.from_user.id, int(msg.text))
    await _show(msg.chat.id, msg.bot, d)
    await state.clear()

@router.callback_query(F.data == "buy_regular")
async def choose_regular(cb: types.CallbackQuery, state):
    gifts = await GiftService.list_regular()

    kb = InlineKeyboardBuilder()
    for g in gifts:
        kb.button(
            text=f"{g['emoji']} {g['price']}⭐",
            callback_data=f"buy_{g['id']}_{g['price']}"
        )
    kb.adjust(3)
    await cb.message.edit_text(
        "Выбери подарок:", reply_markup=kb.as_markup()
    )

@router.callback_query(F.data.regexp(r"^buy_(\d+)_(\d+)$"))
async def buy_exact(cb: types.CallbackQuery):
    gift_id, price = map(int, cb.data.split('_')[1:])
    ok = await GiftService.buy(cb.from_user.id, gift_id, price)
    if ok:
        await cb.answer("🎉 Подарок куплен и отправлен!", show_alert=True)
    else:
        await cb.answer("Не получилось: звёзд мало или Telegram отказал.", show_alert=True)