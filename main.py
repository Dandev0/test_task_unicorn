import asyncio
from aiohttp import web
from parser import args
import logging
import requests
import aiohttp
from Abstractclass import AbstractBase

logging.basicConfig(level='DEBUG')
logger = logging.getLogger()
app = web.Application()
routes = web.RouteTableDef()


class Base(AbstractBase):
    def __init__(self):
        self.url = 'https://cdn.cur.su/api/latest.json'
        self.c = 0

    async def take_valute(self):                 #Получаем первый запрос синхронный. c - счетчик для первого получения информации сразу после старта приложения, в else кол-во минут * указанный период
        while True:
            await asyncio.sleep(.1)
            if self.c < 1:
                a = requests.get(self.url)
                logging.warning('Запрос 1')
                request_1 = a.json()
                app['balances'] = request_1
                self.c = self.c + 1
            else:
                await asyncio.sleep(args.period*60)
                async with aiohttp.ClientSession() as request:
                    request_1 = await request.get(self.url)
                    logging.warning('Запрос 2')
                    request_1 = await request_1.json()
                    app['balances'] = request_1

    async def save_valute(self):  # записываем полученную информацию от апи
        await asyncio.sleep(.1)
        logging.warning('Валюта получена и сохраняется')
        self.new_valute = app['balances']
        return self.new_valute

    async def rub(self):                     # обращение к конкретной валюте для реализации rub/get, usd/get, eur/get
        rub = app['balances']['rates']['RUB']
        return rub

    async def usd(self):
        usd = app['balances']['rates']['USD']
        return usd

    async def eur(self):
        eur = app['balances']['rates']['EUR']
        return eur

    async def sum_valute(self):                           #в этой корутине пересчет баланса для каждой валюты
        await asyncio.sleep(.1)
        self.cf_rub_usd = app['balances']['rates']['RUB']
        self.cf_usd_eur = app['balances']['rates']['USD']
        self.cf_rub_eur = self.cf_rub_usd * self.cf_usd_eur * app['balances']['rates']['EUR']
        self.sum_rub = args.rub + args.usd*self.cf_rub_usd + args.eur*self.cf_rub_eur
        self.sum_usd = args.usd + args.rub/self.cf_rub_usd + args.eur*self.cf_usd_eur
        self.sum_eur = args.eur + args.rub/self.cf_rub_eur + args.usd*self.cf_usd_eur
        self.sum = [self.sum_rub, self.sum_usd, self.sum_eur]
        return self.sum

    async def save_update(self):
        await asyncio.sleep(10)
        self.new_sum = await self.sum_valute()
        return self.new_sum

method = Base()

@routes.get('/rub/get')
async def rub_get(request):
    logger.warning('/rub/get')
    logger.info('give rub valute')
    RUB = await method.rub()
    return web.Response(text=f'Курс рубля к доллару: {RUB}', headers={"content-type": "text/plain"})


@routes.get('/usd/get')
async def usd_get(request):
    logger.warning('/usd/get')
    logger.info('give usd valute')
    USD = await method.usd()
    return web.Response(text=f'Курс доллара: {USD}', headers={"content-type": "text/plain"})


@routes.get('/eur/get')
async def eur_get(request):
    logger.warning('/eur/get')
    logger.info('give eur valute')
    EUR = await method.eur()
    return web.Response(text=f'Курс евро к доллару: {EUR}', headers={"content-type": "text/plain"})


@routes.post('/modify')
async def modify(request):
    logger.warning('/modify')
    key = await request.json()
    dict_modify = {"rub": "0", "usd": "0", "eur": "0"}
    for i in key:
        if i == 'rub':
            item = int(key['rub'])
            logger.info('rub modify')
            dict_modify["rub"] = item
        elif i == 'usd':
            item = int(key['usd'])
            logger.info('usd modify')
            dict_modify["usd"] = item
        elif i == 'eur':
            item = int(key['eur'])
            logger.info('eur modify')
            dict_modify["eur"] = item
    await update(dict_modify)


async def update(dict_modify):
    args.rub += int(dict_modify['rub'])
    args.usd += int(dict_modify['usd'])
    args.eur += int(dict_modify['eur'])


@routes.post('/set')
async def set(request):
    logger.warning('/set')
    key = await request.json()
    dict_set = {"rub": "0", "usd": "0", "eur": "0"}
    for x in key:
        if x == 'rub':
            item = int(key['rub'])
            logger.info('rub set')
            dict_set['rub'] = item
        elif x == 'usd':
            item = int(key['usd'])
            logger.info('usd set')
            dict_set['usd'] = item
        elif x == 'eur':
            item = int(key['eur'])
            logger.info('eur set')
            dict_set['eur'] = item
    await set(dict_set)


async def set(dict_set):
    args.rub = int(dict_set['rub'])
    args.usd = int(dict_set['usd'])
    args.eur = int(dict_set['eur'])


@routes.get('/amount')
async def amount(request):
    logger.warning('/amount')
    sum = await method.sum_valute()
    rub = sum[0]
    usd = sum[1]
    eur = sum[2]
    return web.Response(
        text=f'На балансе: Rub = {args.rub} Usd = {args.usd}, Eur = {args.eur}\nСумма в рублях: {round(rub, 2)}\nСумма в долларах: {round(usd, 2)}\nСумма в евро: {round(eur, 2)}',
        headers={"content-type": "text/plain"})


async def start():
    logger.debug('give args')
    if args.debug.lower() in {'1', 'true', 'y'}:
        request = requests.get('https://cdn.cur.su/api/latest.json')
        print(f'Запрос: https://cdn.cur.su/api/latest.json \nСтатус код: {request.status_code}')
    elif args.debug.lower() in {'0', 'false', 'n'}:
        print('Приложение стартонуло!\nДанные о курсах валют получены!')
    await asyncio.sleep(1)

async def check_update(app):
    while True:
        logging.warning('Вошел в ф-ка чек ап')
        app['balance'] = await method.sum_valute()
        app['valute'] = [method.cf_rub_usd, method.cf_usd_eur, await method.eur()]
        app['check_update_valute'] = [await method.rub(), await method.usd(), await method.eur()]
        if app['balance'] != await method.save_update() or app['valute'] != app['check_update_valute']:   #между sum_valute и save_valute разница 9.9сек, соответственно сравниваются данные записаные до и после истечения 9.9сек
            print('Изменился курс валют или баланс кошелька')
            print('Старый баланс: ', app['balance'],'Ноывй баланс: ', await method.save_update())
            print('Актуальный курс валюты: ',app['check_update_valute'])
        else:
            print('Баланс кошелька и курс не изменились!')
        await asyncio.sleep(60)

async def background_tasks(app):
    app['start'] = asyncio.create_task(start())                  # в ней нет while True, выполнится 1 раз на старте приложения и сама затрется
    app['take_valute'] = asyncio.create_task(method.take_valute())
    app['task'] = asyncio.create_task(check_update(app))

async def _on_shutdown(app):                                     #стоп сервера по КРИТИКАЛ статусу(критикал прописан только тут).
    logging.critical('Server is stoped!')
    await app['task']
    if logging.getLogger().level == logging.CRITICAL:
        app['take_valute'].cancel()
        app['task'].cancel()
        await asyncio.sleep(.5)

def main():
    app.on_startup.append(background_tasks)
    app.add_routes(routes)
    web.run_app(app, host='127.0.1.1', port='8080')
    app.on_shutdown.append(_on_shutdown)

if __name__ == '__main__':
    main()
