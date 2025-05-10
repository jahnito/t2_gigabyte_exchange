from classes import Volume2
import os
import asyncio
from time import sleep, gmtime
from datetime import datetime, timedelta
from database import get_volumes_pg, check_db_pg, insert_volume_pg, clean_data


# Postgres DSN
DB_USER = os.environ.get('PG_USER')
DB_PASSWORD = os.environ.get('PG_PASSWD')
DB_HOST = os.environ.get('PG_HOST')
DB_NAME = os.environ.get('PG_DBNAME')
# DSN = f'dbname=worker user=postgres password=P@sSw0rd host=192.168.3.80'
DSN = f'dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST}'
# Вкл/Отк отрисовки данных на стандартный вывод
RENDER = os.environ.get('RENDER', False)
# Интервал перерисовки данных
RENDER_INTERVAL = 30
# Последняя очистка БД
CLRTIME = 0


def check_env(user, passw, host, name):
    if not user:
        print('Set DB User in env')
        return False
    if not passw:
        print('Set DB Passw in env')
        return False
    if not host:
        print('Set DB Host in env')
        return False
    if not name:
        print('Set DB Name in env')
        return False
    return True


async def set_volumes(dsn:str, render: bool):
    '''
    Функция создает список объемов из БД
    '''
    volumes = await get_volumes_pg(dsn)
    return [Volume2(i, render=render) for i in volumes]


async def volumes_manage(dsn:str, volumes: list[Volume2], render: bool):
    '''
    Функция обновляет список волюмов по изм. в БД
    '''
    actual_volumes = await get_volumes_pg(dsn)
    active_volumes = [i.volume for i in volumes]
    for i in actual_volumes:
        if i not in active_volumes:
            volumes.append(Volume2(i, render=render))
    res = [v for v in volumes if v.volume in actual_volumes]
    res.sort(key=lambda x: x.volume)
    return res


async def cleaning_db(dsn: str):
    global CLRTIME
    if CLRTIME != gmtime().tm_hour:
        print(f'Очистка данных {gmtime().tm_hour}:{gmtime().tm_min}')
        CLRTIME = gmtime().tm_hour
        await clean_data(dsn, 1)


async def main():
    if RENDER:
        render_last = datetime.now()
    volumes = await set_volumes(DSN, render=RENDER)
    while True:
        volumes = await volumes_manage(DSN, volumes, render=RENDER)
        if len(volumes) > 0:
            for v in volumes:
                if v.next_get <= datetime.now():
                    await v.get_volume()
                    await insert_volume_pg(DSN, v)
            await cleaning_db(DSN)
            if RENDER and render_last < datetime.now() - timedelta(seconds=RENDER_INTERVAL):
                os.system('clear')
                render_last = datetime.now()            
                for sh_vol in volumes:
                    print(sh_vol)
        else:
            os.system('clear')
            print('No volumes for monitoring')
            sleep(10)


if __name__ == '__main__':
    if check_env(DB_USER, DB_PASSWORD, DB_HOST, DB_NAME):
        # Проверка базы данных
        asyncio.run(check_db_pg(DSN))
        # Старт основной программы
        asyncio.run(main())
