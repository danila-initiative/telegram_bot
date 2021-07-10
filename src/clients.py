"""Взаимодействие с Airtable"""
import os
from typing import NamedTuple
from airtable import Airtable
import pandas as pd
from pandas.core.frame import DataFrame

class Client(NamedTuple):
    id: str
    key_word: str
    min_price: int
    max_price: int
    location: str

    def __str__(self):
        return f"{self.id} {self.key_word} {self.min_price} {self.max_price} {self.location}"



class AirtableInstance():
    def __init__(self):
        self.base_key = os.environ['BASE_KEY']
        self.table_name = os.environ['TABLE_NAME']
        self.api_key = os.environ['AIRTABLE_API_KEY']
        self._load_table()

    def _load_table(self):
        self.airtable = Airtable(
            self.base_key, self.table_name, api_key=self.api_key)

    # def get_data_as_df(self) -> DataFrame:
    #     records = self.airtable.get_all()
    #     df = pd.DataFrame.from_records(r['fields'] for r in records)
    #     return df
    
    def get_active_clients(self) -> list[Client]:
        records = self.airtable.get_all()
        active_clients = []
        for record in records:
            record = record["fields"]
            if record["subscription"] == "Active":
                active_clients.append(Client(
                    id = record["id"],
                    key_word = record["key_word"],
                    location = record["location"],
                    min_price = record["min_price"],
                    max_price = record["max_price"]
                ))
        
        return active_clients
    
    
if __name__ == "__main__":
    airtable = AirtableInstance()
    clients = airtable.get_active_clients()
    for client in clients:
        print(client)