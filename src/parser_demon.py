import os
import random
import time
from parser import (GetPageByURL, ParseResultPage, RequestFormation,
                    SaveDfToExel)
from pathlib import Path

from loguru import logger

import consts
from clients import AirtableInstance
from dates import FormatDate, GetCurrentDate, GetRequestDates


@logger.catch
def StartParsing():
    """ Парсит сайт и сохраняет результаты в таблички """
    Path(f"{consts.RESULTS_FOLDER}").mkdir(parents=True, exist_ok=True)

    airtable = AirtableInstance()
    clients = airtable.get_active_clients()

    today_results_folder = f"{consts.RESULTS_FOLDER}/{FormatDate(GetCurrentDate())}"
    Path(today_results_folder).mkdir(parents=True, exist_ok=True)

    for client in clients:
        url = RequestFormation(client.key_word, 
                                client.min_price,
                                client.max_price,
                                GetRequestDates().publish_date,
                                client.location
                                )
        
        logger.info(f"id: {client.id}, key word: {client.key_word}, location: {client.location}")
        logger.info(f"url: {url}")

        page = GetPageByURL(url)
        df_results = ParseResultPage(page, client.key_word)
        number_of_records = len(df_results)
        
        file_name = f"{today_results_folder}/{client.id}_{number_of_records}_{client.key_word}_{client.location}.xlsx"
        
        if "\"" in file_name:
            file_name = file_name.replace("\"", "\'")
        logger.info(file_name)
        SaveDfToExel(df_results, file_name)
        time.sleep(random.randint(3, 10))
    
    result_files = os.listdir(today_results_folder)
    logger.info(f"Was saved {len(result_files)} exlel tables with results in \"{today_results_folder}\"")
    
if __name__ == "__main__":
    logger.add(consts.LOG_FILE + "{time:YYYY-MM-DD}.log", format="{time} {level} {message}", 
                level="INFO")
    logger.info(f"=====Скрипт {Path(__file__).name} запустился=====")

    StartParsing()



