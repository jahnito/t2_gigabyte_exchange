from classes import Volume2
import os
import asyncio
from asyncio import sleep
from datetime import datetime
from database import insert_volume


DB = 'worker.db'


async def main():
    v = Volume2(19)
    c = 0
    while True:
        if v.next_get <= datetime.now():
            os.system('clear')
            c += 1
            await v.get_volume()
            await insert_volume(DB, v)
            print(v)
            print(c)



if __name__ == '__main__':
    
    # while True:
    #     os.system('clear')
    #     v.get_volume()
    #     print(v)
    #     time.sleep(10)
    # print(v.url)
    
    # print(v)


    asyncio.run(main())
