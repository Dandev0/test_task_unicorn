from abc import ABC, abstractmethod

class AbstractBase(ABC):

    @abstractmethod
    async def take_valute(self):
        """Раз в -period получает данные о курсе валют(-period задает пользователь при запуске микросервиса)"""

    @abstractmethod
    async def save_update_balance(self):
        """Сохраняет обновленный баланс"""

    @abstractmethod
    async def save_valute(self):
        """Сохраняем валюту, чтобы в последствии производить сравнение и выводить информацию в консоль при ее изменении"""

    @abstractmethod
    async def sum_valute(self):
        """Производим конвертацию баланса в кошелька в каждую из 3 валют"""
