"""
если сейчас больше 8 утра, то:
* получаем таблицу с клиентами
* отбираем только пользователей с активной подпиской
* формируем запросы для всех активных клиентов
* с каким-то рандомным интервалом:
    * делаем запрос
    * получаем страницу
    * парсим её
    * записываем в DF
    * сохраняем в csv
"""
from pandas.core.frame import DataFrame
from airtable import AirtableInstance
import requests
import time
import random
from parser import ParseResultPage, SaveDataFrameToXlsx, GetDataForParser

airtable = AirtableInstance()
clients = airtable.get_active_clients()

for client in clients:
    RequestFormation()
    GetPageByURL()
    ParseResultPage()
    file_name = f"{RESULT_FOLDER}/{today}_{key_word}_{location}_{min_price}_{max_price}.xlsx"
    SaveDfToExel()
    time.sleep(random.randint(3, 10))




