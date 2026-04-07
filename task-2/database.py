import aiosqlite

DB_NAME = "chat.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                room TEXT,
                recipient TEXT,
                text TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def user_exists(username):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT 1 FROM users WHERE username = ?", (username,)) as cursor:
            return await cursor.fetchone() is not None

async def get_or_create_user(username):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM users WHERE username = ?", (username,)) as cursor:
            user = await cursor.fetchone()
        if not user:
            await db.execute("INSERT INTO users (username) VALUES (?)", (username,))
            await db.commit()
            return {"username": username, "is_new": True}
        return {"username": username, "is_new": False}

async def get_or_create_room(name, created_by):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT * FROM rooms WHERE name = ?", (name,)) as cursor:
            room = await cursor.fetchone()
        if not room:
            await db.execute("INSERT INTO rooms (name, created_by) VALUES (?, ?)", (name, created_by))
            await db.commit()
            return {"name": name, "is_new": True}
        return {"name": name, "is_new": False}

async def search_rooms(query):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT name, created_by, created_at FROM rooms WHERE name LIKE ?",
            (f"%{query}%",)
        ) as cursor:
            rows = await cursor.fetchall()
        return [{"name": r[0], "created_by": r[1], "created_at": r[2]} for r in rows]

async def save_message(sender, text, room=None, recipient=None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO messages (sender, room, recipient, text) VALUES (?, ?, ?, ?)",
            (sender, room, recipient, text)
        )
        await db.commit()

async def get_room_history(room, limit=50):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT sender, text, timestamp FROM messages WHERE room = ? ORDER BY timestamp LIMIT ?",
            (room, limit)
        ) as cursor:
            rows = await cursor.fetchall()
        return [{"sender": r[0], "text": r[1], "timestamp": r[2]} for r in rows]

async def get_dm_history(user1, user2, limit=50):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """SELECT sender, recipient, text, timestamp FROM messages
               WHERE (sender = ? AND recipient = ?) OR (sender = ? AND recipient = ?)
               ORDER BY timestamp DESC LIMIT ?""",
            (user1, user2, user2, user1, limit)
        ) as cursor:
            rows = await cursor.fetchall()
        return [{"sender": r[0], "recipient": r[1], "text": r[2], "timestamp": r[3]} for r in reversed(rows)]

async def get_user_rooms(username):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            "SELECT DISTINCT room FROM messages WHERE sender = ? AND room IS NOT NULL",
            (username,)
        ) as cursor:
            rows = await cursor.fetchall()
        return [r[0] for r in rows]

async def get_user_dms(username):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """SELECT DISTINCT
                CASE WHEN sender = ? THEN recipient ELSE sender END as other_user
               FROM messages
               WHERE (sender = ? OR recipient = ?) AND room IS NULL""",
            (username, username, username)
        ) as cursor:
            rows = await cursor.fetchall()
        return [r[0] for r in rows]
