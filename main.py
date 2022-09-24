import asyncio
import json
from aiohttp import web
from parser import args
import logging
import requests
import aiohttp
from Abstractclass import AbstractBase
import warnings

warnings.filterwarnings('ignore')
logging.basicConfig(level='INFO')
logger = logging.getLogger()
app = web.Application()
routes = web.RouteTableDef()


class Base(AbstractBase):
    def __init__(self):
        self.url = 'https://cdn.cur.su/api/latest.json'

    async def take_valute(self):
        while True:
            async with aiohttp.ClientSession() as request:
                response = await request.get(self.url)
                logging.warning('Запрос валют от апи')
                response = response.json()
                app['valute'] = await response
                await asyncio.sleep(args.period * 60)


    async def save_valute(self):                         #записываем полученную информацию от апи позже, чем в корутину сумма валют, чтобы отследить изменения в курсе валют
        await asyncio.sleep(.5)
        logging.warning('Валюта получена и сохраняется')
        self.new_valute = [app['valute']['rates']['RUB'], app['valute']['rates']['USD'], app['valute']['rates']['EUR']]
        return self.new_valute


    async def sum_valute(self):                           #В этой корутине пересчет баланса для каждой валюты
        await asyncio.sleep(.1)
        self.eur = app['valute']['rates']['EUR']
        self.cf_rub_usd =  app['valute']['rates']['RUB']
        self.cf_usd_eur =  app['valute']['rates']['USD']
        self.cf_rub_eur = self.cf_rub_usd * self.cf_usd_eur * self.eur
        self.sum_rub = args.rub + args.usd*self.cf_rub_usd + args.eur*self.cf_rub_eur
        self.sum_usd = args.usd + args.rub/self.cf_rub_usd + args.eur*self.cf_usd_eur
        self.sum_eur = args.eur + args.rub/self.cf_rub_eur + args.usd*self.cf_usd_eur
        self.sum = [self.sum_rub, self.sum_usd, self.sum_eur]
        return self.sum


    async def save_update_balance(self):                 #корутина для записи суммы валют с слипом, чтобы отслеживать изменения в балансе кошелька
        await asyncio.sleep(59)
        self.new_sum = await self.sum_valute()
        return self.new_sum


@routes.get('/rub/get')
async def rub_get(request):
    rub = app['valute']['rates']['RUB']
    logger.debug('give rub valute')
    return web.Response(text=f'Курс рубля к доллару: {rub}', headers={"content-type": "text/plain"})


@routes.get('/usd/get')
async def usd_get(request):
    logger.debug('give usd valute')
    usd = app['valute']['rates']['USD']
    return web.Response(text=f'Курс доллара: {usd}', headers={"content-type": "text/plain"})


@routes.get('/eur/get')
async def eur_get(request):
    logger.debug('give eur valute')
    eur = app['valute']['rates']['EUR']
    return web.Response(text=f'Курс евро к доллару: {eur}', headers={"content-type": "text/plain"})


@routes.post('/modify')
async def modify(request):
    try:
        request_modify = await request.json()
        logging.info(f'Тело запроса: {request_modify}')
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
        args.rub += int(dict_modify['rub'])
        args.usd += int(dict_modify['usd'])
        args.eur += int(dict_modify['eur'])
    except json.decoder.JSONDecodeError:
        print('Вы допустили ошибку в запросе')
        return web.Response(text="Вы допустили ошибку в запросе")


@routes.post('/set')
async def set(request):
    try:
        request_set = await request.json()
        logging.info(f'Тело запроса: {request_set}')
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
        args.rub = int(dict_set['rub'])
        args.usd = int(dict_set['usd'])
        args.eur = int(dict_set['eur'])
    except json.decoder.JSONDecodeError:
        print('Вы допустили ошибку в запросе')
        return web.Response(text="Вы допустили ошибку в запросе")


method = Base()
@routes.get('/amount')
async def amount(request):
    logger.info('amount/get')
    return web.Response(
        text=f'На балансе: Rub = {args.rub} Usd = {args.usd}, Eur = {args.eur}\nСумма в рублях: {round(method.sum_rub, 2)}\nСумма в долларах: {round(method.sum_usd, 2)}\nСумма в евро: {round(method.sum_eur, 2)}',
        headers={"content-type": "text/plain"})


async def start():
    logger.debug('give args')
    if args.debug.lower() in {'1', 'true', 'y'}:
        pass
    elif args.debug.lower() in {'0', 'false', 'n'}:
        await asyncio.sleep(1)
        print(f'Приложение стартонуло!\nДанные о курсах валют получены!\nСумма в рублях: {round(method.sum_rub, 2)}\nСумма в долларах: {round(method.sum_usd, 2)}\nСумма в евро: {round(method.sum_eur, 2)}')
        logger.disabled = True


async def check_update():
    while True:
        await asyncio.sleep(.5)
        sum_valute = await method.sum_valute()
        update_balance = await method.save_update_balance()
        old_valute = [method.cf_rub_usd, method.cf_usd_eur,method.eur]  # данные до записи обновленных устройств
        new_valute = await method.save_valute()
        await asyncio.sleep(.5)
        if sum_valute != update_balance or old_valute != new_valute:   #между sum_valute и update_balance разница, соответственно сравниваются данные записаные до и после истечения слип в save_epdate_balance
            print('Изменился курс валют или баланс кошелька')
            print('Старый баланс: ', sum_valute,'Ноывй баланс: ', update_balance)
            print('Курс валюты: ', new_valute)
        else:
            print('Баланс кошелька и курс не изменились!')


async def background_tasks(app):
    app['take_valute'] = asyncio.create_task(method.take_valute())
    app['start'] = asyncio.create_task(start())                  # в ней нет while True, выполнится 1 раз на старте приложения и сама затрется
    app['task'] = asyncio.create_task(check_update())


async def on_shutdown(app):
    if logging.getLogger().level == logging.CRITICAL:
        logging_level = logging.INFO
        await background_tasks(app).cancel()


def main():
    app.on_startup.append(background_tasks)
    app.add_routes(routes)
    web.run_app(app, host='127.0.1.1', port='8080')
    try:
        app.on_shutdown.append(on_shutdown(app))
    except RuntimeError:
        print('Server is stoped!')


if __name__ == '__main__':
    main()
