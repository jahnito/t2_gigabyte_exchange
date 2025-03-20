from classes import Volume2
import os
import asyncio
from asyncio import sleep
from datetime import datetime, timedelta
from database import insert_volume


# SQLite DB
DB = 'worker.db'
# Список какие значения забирать
WEIGHTS = [5, 19, 26]
# Вкл/Отк отрисовки данных на стандартный вывод
RENDER = True
# Интервал перерисовки данных
RENDER_INTERVAL = 10


async def main():
    if RENDER:
        render_last = datetime.now()
    volumes = [Volume2(i) for i in WEIGHTS]
    while True:
        for v in volumes:
            if v.next_get <= datetime.now():
                await v.get_volume()
                await insert_volume(DB, v)
        if RENDER and render_last < datetime.now() - timedelta(seconds=RENDER_INTERVAL):
            os.system('clear')
            render_last = datetime.now()
            for sh_vol in volumes:
                print(sh_vol)


if __name__ == '__main__':
    asyncio.run(main())
