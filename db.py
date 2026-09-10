import aiosqlite
from datetime import datetime

DB_PATH = "measurements.db"


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                channel TEXT NOT NULL,
                voltage REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        await db.commit()


async def save_measurement(device_id: str, channel: str, voltage: float, timestamp: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO measurements (device_id, channel, voltage, timestamp) VALUES (?, ?, ?, ?)",
            (device_id, channel, voltage, timestamp),
        )
        await db.commit()


async def get_measurements(device_id: str | None = None, since: str | None = None):
    query = "SELECT device_id, channel, voltage, timestamp FROM measurements WHERE 1=1"
    params = []
    if device_id:
        query += " AND device_id = ?"
        params.append(device_id)
    if since:
        query += " AND timestamp >= ?"
        params.append(since)
    query += " ORDER BY timestamp DESC"

    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [
                {"device_id": r[0], "channel": r[1], "voltage": r[2], "timestamp": r[3]}
                for r in rows
            ]