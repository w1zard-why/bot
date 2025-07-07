from dotenv import load_dotenv
load_dotenv()

import asyncio, getpass, os
from telethon import TelegramClient

API_ID   = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
PHONE    = os.getenv("TG_PHONE")
SESSION  = os.getenv("TG_SESSION", "gifts")

async def main():
    client = TelegramClient(SESSION, API_ID, API_HASH)
    await client.start(
        phone=PHONE,
        code_callback=lambda: input("Введите код из Telegram: "),
        password=lambda: input("Пароль 2FA (видимый ввод): ")
    )
    print("✅ Успешно вошли — сессия сохранена:", SESSION)
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
