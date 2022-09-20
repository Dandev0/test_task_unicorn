import aiohttp
import asyncio
from parser import args
from Abstractclass import AbstractBase

class Base(AbstractBase):

    async def take_valute(self):
        await asyncio.sleep(args.period)
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
        cf_rub_usd = await self.rub()
        cf_usd_eur = await self.eur()
        cf_rub_eur = await self.rub() * await self.usd() * await self.eur()
        self.sum_rub = args.rub + args.usd*cf_rub_usd + args.eur*cf_rub_eur
        self.sum_usd = args.usd + args.rub/cf_rub_usd + args.eur*cf_usd_eur
        self.sum_eur = args.eur + args.rub/cf_rub_eur + args.usd*cf_usd_eur
        sum = [self.sum_rub, self.sum_usd, self.sum_eur]
        return sum








