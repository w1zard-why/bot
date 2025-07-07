from app.services.gift_mtproto import client
class GiftStoreAPI:
    async def get_new_gifts(self, after_ts=None):
        await client().start()
        gifts = await client().list_gifts()
        if after_ts:
            gifts = [g for g in gifts if g.date > after_ts]
        return [{"id":g.id, "price":g.stars, "slug":g.slug, "date":g.date} for g in gifts]

    async def purchase(self, user_id, gift_id):
        await client().start()
        gifts = await client().list_gifts()
        g = next(g for g in gifts if g.id == gift_id)
        await client().buy_and_send(g, user_id)
