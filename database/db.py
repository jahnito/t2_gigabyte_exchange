from classes import Volume2
import aiosqlite

__all__ = ['insert_volume']


async def insert_volume(db: str, v: Volume2):
    queries = []
    queries.append(f'INSERT INTO lots (volume, dtime, cnt, region) VALUES ({v.volume}, datetime("now"), {v.last_new_lots}, "{v.region}")')
    queries.append(f'INSERT INTO sold (volume, dtime, cnt, region) VALUES ({v.volume}, datetime("now"), {v.last_sold_lots}, "{v.region}")')
    queries.append(f'INSERT INTO rockets (volume, dtime, cnt, region) VALUES ({v.volume}, datetime("now"), {v.last_rockets}, "{v.region}")')
    try:
        async with aiosqlite.connect(db) as conn:
            for q in queries:
                await conn.execute(q)
            await conn.commit()
    except aiosqlite.Error as e:
        print(e)
