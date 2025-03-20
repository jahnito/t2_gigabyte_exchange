from classes import Volume2
import aiosqlite
import sqlite3

__all__ = ['insert_volume', 'check_db']


async def insert_volume(db: str, v: Volume2):
    queries = []
    queries.append(f'INSERT INTO lots (volume, dtime, cnt, region) VALUES ({v.volume}, datetime("now"), {v.last_new_lots}, "{v.region}")')
    queries.append(f'INSERT INTO sold (volume, dtime, cnt, region) VALUES ({v.volume}, datetime("now"), {v.last_sold_lots}, "{v.region}")')
    queries.append(f'INSERT INTO rockets (volume, dtime, cnt, region) VALUES ({v.volume}, datetime("now"), {v.last_rockets}, "{v.region}")')
    queries.append(f'INSERT INTO coefficients (volume, dtime, ten_min, one_hour, one_day) VALUES ({v.volume}, datetime("now"), {v.coefficient["ten_min"]}, {v.coefficient["one_hour"]}, {v.coefficient["one_day"]})')
    try:
        async with aiosqlite.connect(db) as conn:
            for q in queries:
                await conn.execute(q)
            await conn.commit()
    except aiosqlite.Error as e:
        print(e)


def check_db(db: str):
    with open('setup/db.sql') as sql:
        script = sql.read()
    try:
        with sqlite3.connect(db) as conn:
            conn.executescript(script)
            conn.commit()
    except sqlite3.Error as e:
        print(e)
