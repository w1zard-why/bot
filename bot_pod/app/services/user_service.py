# app/services/user_service.py
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parents[2] / "data" / "bot.db"
DB_FILE.parent.mkdir(exist_ok=True)

def _conn():
    return sqlite3.connect(DB_FILE)

def _init():
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT,
            stars INTEGER DEFAULT 0,
            autobuy INTEGER DEFAULT 0,
            max_price INTEGER DEFAULT 100,
            max_qty INTEGER DEFAULT 3
        )""")
_init()


class UserService:
    @staticmethod
    async def register(uid: int, username: str | None):
        with _conn() as c:
            c.execute("INSERT OR IGNORE INTO users(id, username) VALUES(?,?)",
                      (uid, username))

    @staticmethod
    async def add_stars(uid: int, amount: int):
        with _conn() as c:
            c.execute("UPDATE users SET stars = stars + ? WHERE id = ?",
                      (amount, uid))

    @staticmethod
    async def spend_stars(uid: int, amount: int):
        with _conn() as c:
            cur = c.execute("SELECT stars FROM users WHERE id = ?", (uid,))
            row = cur.fetchone()
            if not row or row[0] < amount:
                raise ValueError("Недостаточно звёзд")
            c.execute("UPDATE users SET stars = stars - ? WHERE id = ?",
                      (amount, uid))

    @staticmethod
    async def set_autobuy(uid: int, flag: bool):
        with _conn() as c:
            c.execute("UPDATE users SET autobuy = ? WHERE id = ?",
                      (1 if flag else 0, uid))

    @staticmethod
    async def set_autobuy_settings(uid: int, max_price: int, max_qty: int):
        with _conn() as c:
            c.execute("UPDATE users SET max_price=?, max_qty=? WHERE id=?",
                      (max_price, max_qty, uid))

    @staticmethod
    async def get_stars(uid: int) -> int:
        with _conn() as c:
            cur = c.execute("SELECT stars FROM users WHERE id = ?", (uid,))
            row = cur.fetchone()
            return row[0] if row else 0
    
    @staticmethod
    async def get_settings(uid):
        with _conn() as c:
            row = c.execute(
                "SELECT autobuy, max_price, max_qty FROM users WHERE id=?",
                (uid,)
            ).fetchone()
        return dict(autobuy=bool(row[0]), max_price=row[1], max_qty=row[2])

    @staticmethod
    async def toggle_autobuy(uid):
        with _conn() as c:
            cur = c.execute(
                "UPDATE users SET autobuy = 1 - autobuy WHERE id=? "
                "RETURNING autobuy,max_price,max_qty",
                (uid,)
            )
            a, p, q = cur.fetchone()
        return dict(autobuy=bool(a), max_price=p, max_qty=q)

    @staticmethod
    async def set_price(uid, price):
        with _conn() as c:
            c.execute("UPDATE users SET max_price=? WHERE id=?", (price, uid))
        return await UserService.get_settings(uid)

    @staticmethod
    async def set_qty(uid, qty):
        with _conn() as c:
            c.execute("UPDATE users SET max_qty=? WHERE id=?", (qty, uid))
        return await UserService.get_settings(uid)

    @staticmethod
    async def try_spend(uid: int, amount: int) -> bool:
        with _conn() as c:
            cur = c.execute("SELECT stars FROM users WHERE id=?", (uid,))
            row = cur.fetchone()
            if not row or row[0] < amount:
                return False
            c.execute("UPDATE users SET stars = stars - ? WHERE id = ?", (amount, uid))
        return True