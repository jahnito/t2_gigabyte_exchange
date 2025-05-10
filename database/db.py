from classes import Volume2
import aiosqlite
import sqlite3
import aiopg


__all__ = [
    'insert_volume_sqlite', 'get_volumes_sqlite', 'check_db_sqlite',
    'get_volumes_pg', 'check_db_pg', 'insert_volume_pg', 'clean_data'
    ]


async def get_volumes_pg(dsn):
    query = 'SELECT volume FROM volumes;'
    pool = await aiopg.create_pool(dsn)
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)
                ret = await cursor.fetchall()
            await conn.close()
        return tuple(i[0] for i in ret)
    except aiosqlite.Error as e:
        print(e)
        return None


async def check_db_pg(dsn):
    with open('setup/db_pg.sql') as sql:
        script = sql.read()
    pool = await aiopg.create_pool(dsn)
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(script)
                await conn.close()
    except Exception as e:
        print(e)


async def insert_volume_pg(dsn, v: Volume2):
    queries = []
    queries.append(f'INSERT INTO lots (volume, dtime, cnt, region) VALUES ({v.volume}, NOW(), {len(v.last_new_lots)}, \'{v.region}\');')
    queries.append(f'INSERT INTO rockets (volume, dtime, cnt, region) VALUES ({v.volume}, NOW(), {len(v.last_rockets)}, \'{v.region}\');')
    queries.append(f'INSERT INTO anomaly (volume, dtime, cnt, region) VALUES ({v.volume}, NOW(), {len(v.last_anomaly_lots)}, \'{v.region}\');')
    queries.append(f'INSERT INTO sold (volume, dtime, cnt, region) VALUES ({v.volume}, NOW(), {len(v.last_sold_lots)}, \'{v.region}\');')
    # queries.append('DELETE FROM anomaly WHERE dtime < NOW() - INTERVAL \'60 minutes\';')
    # queries.append('DELETE FROM lots WHERE dtime < NOW() - INTERVAL \'60 minutes\';')
    # queries.append('DELETE FROM rockets WHERE dtime < NOW() - INTERVAL \'60 minutes\';')
    # queries.append('DELETE FROM sold WHERE dtime < NOW() - INTERVAL \'60 minutes\';')
    pool = await aiopg.create_pool(dsn)
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                for q in queries:
                    await cursor.execute(q)
            await conn.close()
    except Exception as e:
        print(e)


async def clean_data(dsn: str, interval: int):
    pool = await aiopg.create_pool(dsn)
    tables = ['lots', 'anomaly', 'rockets', 'sold']
    try:
        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                for tbl in tables:
                    await cursor.execute(f"DELETE FROM {tbl} WHERE dtime < NOW() - INTERVAL '{interval} hours'")
            await conn.close()
    except Exception as e:
        print(e)


async def get_volumes_sqlite(db: str):
    query = 'SELECT volume FROM volumes'
    try:
        async with aiosqlite.connect(db) as conn:
            cursor = await conn.execute(query)
            result = await cursor.fetchall()
        return tuple(i[0] for i in result)
    except aiosqlite.Error as e:
        print(e)
        return None


async def insert_volume_sqlite(db: str, v: Volume2):
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


def check_db_sqlite(db: str):
    with open('setup/db_sqlite.sql') as sql:
        script = sql.read()
    try:
        with sqlite3.connect(db) as conn:
            conn.executescript(script)
            conn.commit()
    except sqlite3.Error as e:
        print(e)


