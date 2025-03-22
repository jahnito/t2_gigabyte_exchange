import aiohttp
from datetime import datetime, timedelta
from tabulate import tabulate
from random import randint



class Volume2():
    '''
    Class for aiohttp
    '''
    def __init__(self, volume: int, price: int = 15,
                 offset: int = 0, limit:int = 250,
                 timeout: int = 5, region: str = 'perm',
                 url: str = '.t2.ru/api/exchange/lots?',
                 headers={'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'}):
        self.volume = volume
        self.region = region
        self.url = f'https://{region}{url}'
        self.params = {'trafficType': 'data',
                       'volume': volume,
                       'cost': volume * price,
                       'offset': offset,
                       'limit': limit}
        self.headers: dict = headers
        self.timeout = timeout
        self.next_get = datetime.now()
        self.cnt_added_lots: dict = {}
        self.cnt_sold_lots: dict = {}
        self.cnt_rockets: dict = {}
        self.last_new_lots: list = []
        self.last_sold_lots: list = []
        self.last_rockets: list = []
        self.last_block: int = 0
        self.last_time = datetime.now()
        self.new_lots: list = None
        self.prev_lots: list = None
        self.coefficient: dict = {'ten_min': 0, 'one_hour': 0, 'one_day': 0}

    async def get_volume(self):
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(self.url, params=self.params) as resp:
                    status = resp.status
                    data = await resp.json()
            if status == 200 and data:
                self.prev_lots = self.new_lots
                self.new_lots = tuple(lot for lot in data['data'])
                self.last_time = datetime.now()
                self.count_new_lots()
                # self.count_rockets()
                self.count_sold_lots()
                self.get_coefficient()
                self.clear_old_data()
                # self.next_get = self.last_time + timedelta(seconds=(self.timeout + randint(1, 3)))
                self.next_get = self.last_time + timedelta(seconds=(self.timeout))
        except aiohttp.ClientError as e:
            print(e)

    def count_new_lots(self):
        if self.prev_lots and self.new_lots:
            self.last_new_lots = []
            self.last_rockets = []
            nl = [i['id'] for i in self.new_lots]
            pl = [i['id'] for i in self.prev_lots]

            # Ищем индекс до которого навалили ракеты и новые лоты
            # Поэлементно ищем первый или последующий лот в новом массиве
            for i in pl:
                if i in nl:
                    crop_index = nl.index(i)
                    pl = pl[:-crop_index]
                    break
            
            # Если в этой пачке есть объекты из старого массива,
            # объявляем их ракетами, иначе новыми лотами
            for i in nl[:crop_index]:
                if i not in pl:
                    self.last_new_lots.append(i)
                else:
                    self.last_rockets.append(i)

            # for lot in nl:
            #     if lot not in pl:
            #         self.last_new_lots.append(lot)
            #     else:
            #         break
            self.last_block = crop_index
            self.cnt_added_lots[self.last_time] = len(self.last_new_lots)
            self.cnt_rockets[self.last_time] = len(self.last_rockets)

    # def count_rockets(self) -> int:
    #     if self.prev_lots and self.new_lots:
    #         self.last_rockets = []
    #         nl = [i['id'] for i in self.new_lots]
    #         pl = [i['id'] for i in self.prev_lots]
    #         if self.last_new_lots:
    #             nl = nl[len(self.last_new_lots):]
    #         for n, lot in enumerate(nl, len(self.last_new_lots)):
    #             if lot in pl and pl.index(lot) > n + len(self.last_rockets):
    #                 self.last_rockets.append(lot)
    #         self.cnt_rockets[self.last_time] = len(self.last_rockets)

    def count_sold_lots(self) -> int:
        if self.prev_lots and self.new_lots:
            self.last_sold_lots = []
            nl = [i['id'] for i in self.new_lots]
            pl = [i['id'] for i in self.prev_lots]
            if self.last_block:
                pl = pl[:-self.last_block]
            for lot in pl:
                if lot not in nl[self.last_block:] and lot not in self.last_rockets:
                    self.last_sold_lots.append(lot)
            self.cnt_sold_lots[self.last_time] = len(self.last_sold_lots)

    def __repr__(self):
        header = ('Vol:' + str(self.volume), 'Diff', '10 min', '1 hour', '1 day')
        lines = [('New Lots',self.last_new_lots, self.get_sum_new_lots(timedelta(minutes=10)), self.get_sum_new_lots(timedelta(minutes=60)), self.get_sum_new_lots(timedelta(days=1))),
                 ('Sold Lots', self.last_sold_lots, self.get_sum_sold_lots(timedelta(minutes=10)), self.get_sum_sold_lots(timedelta(minutes=60)), self.get_sum_sold_lots(timedelta(days=1))),
                 ('Rockets', self.last_rockets, self.get_sum_rockets(timedelta(minutes=10)), self.get_sum_rockets(timedelta(minutes=60)), self.get_sum_rockets(timedelta(days=1))),
                 ('Coefficient', '---', self.coefficient["ten_min"], self.coefficient["one_hour"], self.coefficient["one_day"])
                 ]
        return tabulate(lines, headers=header) + '\n'

    def get_sum_new_lots(self, t: timedelta):
        '''
        Возвращаем количество новых лотов
        '''
        behind_time = datetime.now() - t
        return sum([i for dt, i in self.cnt_added_lots.items() if dt >= behind_time])

    def get_sum_rockets(self, t: timedelta):
        '''
        Возращаем количество ракет
        '''
        behind_time = datetime.now() - t
        return sum([i for dt, i in self.cnt_rockets.items() if dt >= behind_time])

    def get_sum_sold_lots(self, t: timedelta):
        '''
        Возвращаем количество проданных лотов
        '''
        behind_time = datetime.now() - t
        return sum([i for dt, i in self.cnt_sold_lots.items() if dt >= behind_time])

    def get_coefficient(self):
        '''
        Обновляем коэффициенты на текущем запросе
        '''
        deltas = {'ten_min': timedelta(minutes=10),
                  'one_hour': timedelta(hours=1),
                  'one_day': timedelta(days=1)}

        for delta in deltas:
            lots = self.get_sum_new_lots(deltas[delta])
            rockets = self.get_sum_rockets(deltas[delta])
            sum_lots_rockets = lots + rockets
            sold = self.get_sum_sold_lots(deltas[delta])
            if sum_lots_rockets:
                self.coefficient[delta] = round(sold / (lots + rockets), 3)

    def clear_old_data(self):
        '''
        Очистка словаря от данных которым более 24 часов
        '''
        behind_date = datetime.now() - timedelta(days=1)
        for dt in [i for i in self.cnt_added_lots.keys() if i <= behind_date]:
            del self.cnt_added_lots[dt]
        for dt in [i for i in self.cnt_sold_lots.keys() if i <= behind_date]:
            del self.cnt_sold_lots[dt]
        for dt in [i for i in self.cnt_rockets.keys() if i <= behind_date]:
            del self.cnt_rockets[dt]

    def create_table_compare(self, cut_down=True):
        header = ('Number', 'PrevLot', 'Status', 'Number', 'NewLot', 'Status')
        result = []
        rockets = {}
        c = 1
        if self.prev_lots:
            nl = [i['id'] for i in self.new_lots]
            pl = [i['id'] for i in self.prev_lots]
            for n, t in enumerate(zip(pl, nl), 1):
                c += 1
                if t[0] in self.last_sold_lots:
                    prev_status = 'Sold'
                elif t[0] in self.last_rockets:
                    prev_status = f'Rocket  ({rockets[t[0]]})'
                else:
                    prev_status = ''
                if t[1] in self.last_new_lots:
                    new_status = 'New'
                elif t[1] in self.last_rockets:
                    rockets[t[1]] = n
                    new_status = f'Rocket'
                else:
                    new_status = ''
                if cut_down:
                    if prev_status or new_status or c <= 10:
                        result.append([n, t[0], prev_status, n, t[1], new_status])
                else:
                    result.append([n, t[0], prev_status, n, t[1], new_status])
        return tabulate(result, headers=header)
