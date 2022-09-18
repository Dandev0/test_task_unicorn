import aiohttp
import asyncio
from val import args


class Base:
    async def take_valute(self):
        # await asyncio.sleep(args.period)
        url = 'https://cdn.cur.su/api/latest.json'
        async with aiohttp.ClientSession() as request:
            request_1 = await request.get(url)
            request_1 = await request_1.json()
            return request_1

    async def rub(self):
        qwe = await self.take_valute()
        rub = qwe['rates']['RUB']
        return rub

    async def usd(self):
        qwe = await self.take_valute()
        usd = qwe['rates']['USD']
        return usd

    async def eur(self):
        qwe = await self.take_valute()
        eur = qwe['rates']['EUR']
        return eur

    async def sum_valute(self):
        rub = await self.rub()
        usd = await self.usd()
        eur = await self.eur()
        sum_rub = args.rub + (args.usd * rub) + (args.eur * eur * rub)
        sum_usd = args.rub/usd + args.usd + (args.eur*usd)
        sum_eur = args.eur + (args.rub/usd)*eur + (args.usd*eur)
        sum = [sum_rub, sum_usd, sum_eur]
        return sum

