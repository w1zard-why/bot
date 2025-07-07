from datetime import datetime
from app.db import db
from app.api.gift_store import GiftStoreAPI
from app.services.user_service import UserService

async def process_autobuy():
    gifts = await GiftStoreAPI.get_new_gifts()   # свежие редкие подарки
    users = await db.User.filter(autobuy=True)

    for user in users:
        s = user.autobuy_settings or {"max_price": 100, "max_qty": 3}
        bought = 0

        for gift in gifts:
            if gift.price > s["max_price"] or bought >= s["max_qty"]:
                continue

            if user.stars_balance < gift.price:
                break

            # списываем звёзды + покупаем
            await UserService.spend_stars(user.id, gift.price)
            await GiftStoreAPI.purchase(user.id, gift.id)

            await db.Purchase.create(
                user=user, gift_id=gift.id, price=gift.price,
                timestamp=datetime.utcnow()
            )
            bought += 1
