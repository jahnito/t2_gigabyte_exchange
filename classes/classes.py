import aiohttp
from datetime import datetime, timedelta
from tabulate import tabulate
from random import randint



class Volume2():
    '''
    Class for aiohttp
    '''
    def __init__(self, volume: int, price: int = 15,
                 offset: int = 0, limit: int = 500,
                 limit_sold: int = 30,
                 timeout: int = 2, region: str = 'perm',
                 url: str = '.t2.ru/api/exchange/lots?',
                 headers={'User-agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'},
                 wide_view: bool = False,
                 render: bool = False
                 ):
        self.volume = volume
        self.region = region
        self.url = f'https://{region}{url}'
        self.params = {'trafficType': 'data',
                       'volume': volume,
                       'cost': volume * price,
                       'offset': offset,
                       'limit': limit}
        self.limit_sold = limit_sold
        self.headers: dict = headers
        self.timeout = timeout
        self.wide_view = wide_view
        self.next_get = datetime.now()
        self.cnt_added_lots: dict = {}      # Словарь с добавленными лотами
        self.cnt_sold_lots: dict = {}       # Словарь с проданными лотами
        self.cnt_rockets: dict = {}         # Словарь с ракетами
        self.cnt_anomaly_lots: dict = {}    # Словарь с аномальными лотами
        self.last_new_lots: list = []       # Новые лоты
        self.last_sold_lots: list = []      # Проданные лоты
        self.last_rockets: list = []        # Лоты - ракеты
        self.last_anomaly_lots: list = []   # Аномальные лоты (внутри объема)
        self.last_block: int = 0            # Количество доб. лотов и ракет
        self.last_time = datetime.now()
        self.new_lots: list = None
        self.prev_lots: list = None
        self.coefficient: dict = {'ten_min': 0, 'one_hour': 0, 'one_day': 0}
        self.render = render

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
                self._count_new_lots()
                self._count_sold_lots()
                self._count_anomaly_lots()
                if self.render:
                    self.get_coefficient()
                self.clear_old_data()
                self.next_get = self.last_time + timedelta(seconds=(self.timeout), milliseconds=(randint(300, 800)))
        except aiohttp.ClientError as e:
            print(e)

    def _count_new_lots(self):
        if self.prev_lots and self.new_lots:
            crop_index = 0
            self.last_new_lots = []
            self.last_rockets = []
            self.last_anomaly_lots = []
            nl = [i['id'] for i in self.new_lots]
            pl = [i['id'] for i in self.prev_lots]
            for i in pl:
                if i in nl:
                    crop_index = nl.index(i)
                    break

            if crop_index:
                for n in nl[:crop_index]:
                    if n not in pl:
                        self.last_new_lots.append(n)
                    else:
                        self.last_rockets.append(n)

            self.last_block = crop_index
            if self.render:
                self.cnt_added_lots[self.last_time] = len(self.last_new_lots)
                self.cnt_rockets[self.last_time] = len(self.last_rockets)

    def _count_sold_lots(self) -> list:
        if self.prev_lots and self.new_lots:
            self.last_sold_lots = []
            nl = [i['id'] for i in self.new_lots[:self.limit_sold]]
            pl = [i['id'] for i in self.prev_lots[:self.limit_sold]]
            if self.last_block:
                pl = pl[:-self.last_block]
            for lot in pl:
                if lot not in nl[self.last_block:] and lot not in self.last_rockets:
                    self.last_sold_lots.append(lot)
            if self.render:
                self.cnt_sold_lots[self.last_time] = len(self.last_sold_lots)

    def _count_anomaly_lots(self) -> list:
        if self.prev_lots and self.new_lots:
            # Определяем аномальные лоты
            nl = [i['id'] for i in self.new_lots]
            pl = [i['id'] for i in self.prev_lots]
            if self.last_sold_lots:
                nl = nl[:-len(self.last_sold_lots)]
            for a in nl[self.last_block:]:
                if a not in pl:
                    self.last_anomaly_lots.append(a)
            if self.render:
                self.cnt_anomaly_lots[self.last_time] = len(self.last_anomaly_lots)

    def __repr__(self):
        if self.wide_view:
            comp_table = self.create_table_compare()
        else:
            comp_table = ''
        header = ('Vol:' + str(self.volume), 'Diff', '10 min', '1 hour', '1 day')
        lines = [('New Lots', len(self.last_new_lots), self.get_sum_new_lots(timedelta(minutes=10)), self.get_sum_new_lots(timedelta(minutes=60)), self.get_sum_new_lots(timedelta(days=1))),
                 ('Sold Lots', len(self.last_sold_lots), self.get_sum_sold_lots(timedelta(minutes=10)), self.get_sum_sold_lots(timedelta(minutes=60)), self.get_sum_sold_lots(timedelta(days=1))),
                 ('Rockets', len(self.last_rockets), self.get_sum_rockets(timedelta(minutes=10)), self.get_sum_rockets(timedelta(minutes=60)), self.get_sum_rockets(timedelta(days=1))),
                 ('Anomaly', len(self.last_anomaly_lots), self.get_sum_anomaly_lots(timedelta(minutes=10)), self.get_sum_anomaly_lots(timedelta(minutes=60)), self.get_sum_anomaly_lots(timedelta(days=1))),
                 ('Coefficient', '---', self.coefficient["ten_min"], self.coefficient["one_hour"], self.coefficient["one_day"])
                 ]
        return tabulate(lines, headers=header) + f'\n{comp_table}'

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

    def get_sum_anomaly_lots(self, t: timedelta):
        '''
        Возвращаем количество аномальных
        '''
        behind_time = datetime.now() - t
        return sum([i for dt, i in self.cnt_anomaly_lots.items() if dt >= behind_time])

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
            anomaly = self.get_sum_anomaly_lots(deltas[delta])
            sum_lots_rockets = lots + rockets + anomaly
            sold = self.get_sum_sold_lots(deltas[delta])
            if sum_lots_rockets:
                self.coefficient[delta] = round(sold / (lots + rockets), 3)
            elif sold > 0 and sum_lots_rockets == 0:
                self.coefficient[delta] = sold

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

    def create_table_compare(self, cut_down: bool=True):
        header = ('Number', 'PrevLot', 'Status', 'Number', 'NewLot', 'Status')
        result = []
        rockets = {}
        c = 0
        if self.prev_lots:
            nl = [i['id'] for i in self.new_lots]
            pl = [i['id'] for i in self.prev_lots]
            for n, t in enumerate(zip(pl, nl), 1):
                c += 1
                if t[0] in self.last_sold_lots:
                    prev_status = 'Sold'
                elif t[0] in self.last_rockets:
                    prev_status = f'Rocket'
                else:
                    prev_status = ''
                if t[1] in self.last_anomaly_lots: # and t[1] in self.last_new_lots:
                    new_status = 'New Anomaly'
                # elif t[1] in self.last_anomaly_lots and t[1] in self.last_rockets:
                #     new_status = 'Rocket Anomaly'
                elif t[1] in self.last_new_lots:
                    new_status = 'New'
                elif t[1] in self.last_rockets:
                    rockets[t[1]] = n
                    new_status = f'Rocket'
                else:
                    new_status = ''
                if cut_down:
                    if prev_status or new_status or c <= 20:
                        result.append([n, t[0], prev_status, n, t[1], new_status])
                else:
                    result.append([n, t[0], prev_status, n, t[1], new_status])
        return tabulate(result, headers=header)
