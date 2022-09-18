import asyncio
from aiohttp import web
from methods import Base
from val import args
import aiohttp

app = web.Application()
routes = web.RouteTableDef()

method = Base()

@routes.get('/rub/get')
async def eur_get(request):
    rub = await method.rub()
    return web.Response(text=f'{rub}')


@routes.get('/usd/get')
async def eur_get(request):
    usd = await method.usd()
    return web.Response(text=f'{usd}')


@routes.get('/eur/get')
async def eur_get(request):
    eur = await method.eur()
    return web.Response(text=f'{eur}, {args.period}')


@routes.post('/post')                 #начальный объем средств ДОРАБОТАТЬ ДЛЯ ВСЕХ ВАЛЮТ!
async def set_rub(request):
    async with aiohttp.ClientSession() as session:
        resp = session.post('http://127.0.0.1:8080/post', headers={'Content-Type':'application/json'})
        return web.Response(text=f'Вы отправили\n as643513234867849878784651313321131325135311456465456456456456d{resp}')

@routes.get('/amount')
async def amount(request):
    sum = await method.sum_valute()
    rub = sum[0]
    usd = sum[1]
    eur = sum[2]
    return web.Response(text=f'На балансе: Rub = {args.rub} Usd = {args.usd}, Eur = {args.eur}\nСумма в рублях: {round(rub,2)}\nСумма в долларах: {round(usd,2)}\nСумма в евро: {round(eur,2)}')






if __name__ == "__main__":
    app.add_routes(routes)
    web.run_app(app, host='127.0.0.1', port='8080')
