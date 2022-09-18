import requests
import time
start_time = time.time()
import asyncio

def request():
    с = 0
    while True:
        url = 'http://127.0.0.1:8080/post'
        a = requests.post(url=url)
        print(a.status_code)
        print(a.text)
        print("--- %s seconds ---" % (time.time() - start_time))
        print(f'Запрос номер: {с}')
        с += 1
request()