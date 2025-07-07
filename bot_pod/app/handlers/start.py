from aiogram import Router, types
from aiogram.filters import CommandStart
from app.services.user_service import UserService

router = Router()

@router.message(CommandStart())
async def start_handler(msg: types.Message):
    user = await UserService.register(msg.from_user.id, msg.from_user.username)
    await msg.answer("👋 Добро пожаловать!\n\nИспользуй меню, чтобы управлять своим балансом и автопокупками.")
