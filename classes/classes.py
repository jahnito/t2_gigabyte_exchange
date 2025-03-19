import aiohttp
from datetime import datetime, timedelta


class Volume2():
    '''
    Class for aiohttp
    '''
    def __init__(self, volume: int, price: int = 15,
                 offset: int = 0, limit:int = 30,
                 timeout: int = 10, region: str = 'perm',
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
        self.last_new_lots: int = 0
        self.last_sold_lots: int = 0
        self.last_rockets: int = 0
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
                self.count_sold_lots()
                self.count_rockets()
                self.get_coefficient()
                self.clear_old_data()
                self.next_get = self.last_time + timedelta(seconds=self.timeout)
        except aiohttp.ClientError as e:
            print(e)

    def count_new_lots(self):
        if self.prev_lots and self.new_lots:
            res = 0
            self.last_new_lots = 0
            nl = [i['id'] for i in self.new_lots]
            pl = [i['id'] for i in self.prev_lots]
            for lot in nl:
                if lot not in pl:
                    res += 1
                else:
                    break
            if res:
                self.last_new_lots = res
                self.cnt_added_lots[self.last_time] = res

    def count_sold_lots(self) -> int:
        if self.prev_lots and self.new_lots:
            res = 0
            self.last_sold_lots = 0
            nl = [i['id'] for i in self.new_lots]
            pl = [i['id'] for i in self.prev_lots]
            if self.last_new_lots:
                pl = pl[:-self.last_new_lots]
            for lot in pl:
                if lot not in nl[self.last_new_lots:]:
                    res += 1
            if res:
                self.last_sold_lots = res
                self.cnt_sold_lots[self.last_time] = res

    def count_rockets(self) -> int:
        if self.prev_lots and self.new_lots:
            self.last_rockets = 0
            res = 0
            self.last_sold_lots = 0
            nl = [i['id'] for i in self.new_lots]
            pl = [i['id'] for i in self.prev_lots]
            if self.last_new_lots:
                nl = nl[self.last_new_lots:]
            for n, lot in enumerate(nl, self.last_new_lots):
                if lot in pl and pl.index(lot) > n + res:
                    res += 1
            if res:
                self.last_rockets = res
                self.cnt_rockets[self.last_time] = res

    def __repr__(self):
        repr_data = f'Vol: {self.volume}\n'\
                    f'Added 10 min: {self.get_sum_new_lots(timedelta(minutes=10))} | 1 hour: {self.get_sum_new_lots(timedelta(minutes=60))} | 1 day: {self.get_sum_new_lots(timedelta(days=1))} | Last {self.last_new_lots}\n'\
                    f'Sold 10 min: {self.get_sum_sold_lots(timedelta(minutes=10))} | 1 hour: {self.get_sum_sold_lots(timedelta(minutes=60))} | 1 day: {self.get_sum_sold_lots(timedelta(days=1))} | Last {self.last_sold_lots}\n'\
                    f'Rockets 10 min: {self.get_sum_rockets(timedelta(minutes=10))} | 1 hour: {self.get_sum_rockets(timedelta(minutes=60))} | 1 day: {self.get_sum_rockets(timedelta(days=1))} | Last {self.last_rockets}\n'\
                    f'Coef 10 min: {self.coefficient["ten_min"]} | 1 hour: {self.coefficient["one_hour"]} | 1 day: {self.coefficient["one_day"]}'
        return repr_data

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
