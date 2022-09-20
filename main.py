import asyncio
from aiohttp import web
from methods import Base
from parser import args
import logging
import requests

app = web.Application()
routes = web.RouteTableDef()
method = Base()
logging.basicConfig(level='DEBUG')
logger = logging.getLogger()

@routes.get('/rub/get')
async def eur_get(request):
    logger.warning('/rub/get')
    logger.info('give rub valute')
    RUB = await method.rub()
    return web.Response(text=f'Курс рубля к доллару: {RUB}', headers={"content-type": "text/plain"})

@routes.get('/usd/get')
async def eur_get(request):
    logger.warning('/usd/get')
    logger.info('give usd valute')
    USD = await method.usd()
    return web.Response(text=f'Курс доллара: {USD}', headers={"content-type": "text/plain"})


@routes.get('/eur/get')
async def eur_get(request):
    logger.warning('/eur/get')
    logger.info('give eur valute')
    EUR = await method.eur()
    return web.Response(text=f'Курс евро к доллару: {EUR}, headers={"content-type":"text/plain"}')


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

if __name__ == '__main__':
    async def start():
        logger.debug('give args')
        if args.debug.lower() in {'1', 'true', 'y'}:
            request = requests.get('https://cdn.cur.su/api/latest.json')
            print(f'Запрос: https://cdn.cur.su/api/latest.json \nСтатус код: {request.status_code}')
        elif args.debug.lower() in {'0', 'false', 'n'}:
            print('Приложение стартонуло!\nДанные о курсах валют получены!')
        await asyncio.sleep(5)
        while True:
            logger.warning('give amount')
            sum = await method.sum_valute()
            rub = sum[0]
            usd = sum[1]
            eur = sum[2]
            print(f'На балансе: Rub = {args.rub} Usd = {args.usd}, Eur = {args.eur}\nСумма в рублях: {round(rub, 2)}\nСумма в долларах: {round(usd, 2)}\nСумма в евро: {round(eur, 2)}')
            await asyncio.sleep(55)

    async def background_task(app):
        app['redis_listener'] = asyncio.create_task(start())
        yield
        app['redis_listener'].cancel()
        await app['redis_listener']

    app.add_routes(routes)
    app.cleanup_ctx.append(background_task)
    web.run_app(app, host='127.0.1.1', port='8080')








