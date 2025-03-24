from classes import Volume2
import os
import asyncio
# from asyncio import sleep
from time import sleep
from datetime import datetime, timedelta
from database import insert_volume, check_db, get_volumes


# SQLite DB
DB = 'worker.db'
# Какие объемы мониторим
# WEIGHTS = [5, 19, 26]
# Вкл/Отк отрисовки данных на стандартный вывод
RENDER = True
# Интервал перерисовки данных
RENDER_INTERVAL = 2


async def set_volumes(db:str):
    '''
    Функция создает список объемов из БД
    '''
    volumes = await get_volumes(db)
    return [Volume2(i) for i in volumes]


async def volumes_manage(db:str, volumes: list[Volume2]):
    '''
    Функция обновляет список волюмов по изм. в БД
    '''
    actual_volumes = await get_volumes(db)
    active_volumes = [i.volume for i in volumes]
    for i in actual_volumes:
        if i not in active_volumes:
            volumes.append(Volume2(i))
    res = [v for v in volumes if v.volume in actual_volumes]
    res.sort(key=lambda x: x.volume)
    return res


async def main():
    if RENDER:
        render_last = datetime.now()
    # volumes = [Volume2(i, wide_view=False) for i in WEIGHTS]
    volumes = await set_volumes(DB)
    while True:
        volumes = await volumes_manage(DB, volumes)
        if len(volumes) > 0:
            for v in volumes:
                if v.next_get <= datetime.now():
                    await v.get_volume()
                    # await insert_volume(DB, v)
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
    # Проверка базы данных
    check_db(DB)
    asyncio.run(main())
