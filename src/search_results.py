""""Работа с результатами поиска - добавление, статистика"""

from typing import List, NamedTuple, Optional

from numpy import number
import db

class Purchase(NamedTuple):
    user_id: str
    key_word: str
    publish_date: str
    finish_date: str
    number_of_purchase: str
    subject_of_purchase: str
    price: int
    link: str
    customer: str
    location: str


def add_purchase(purchase: Purchase):
    """Добавляет закупку в базу"""

    db.insert("results", {
        "user_id": purchase.user_id,
        "key_word": purchase.key_word,
        "publish_date": purchase.publish_date,
        "finish_date": purchase.finish_date,
        "number_of_purchase": purchase.number_of_purchase,
        "subject_of_purchase": purchase.subject_of_purchase,
        "price": purchase.price,
        "link": purchase.link,
        "customer": purchase.customer,
        "location": purchase.location
    })  

def get_results(user_id: str, publish_date: str, key_word: str) -> List[Purchase]:
    """Возвращает результаты """
    cursor = db.get_cursor()
    cursor.execute(f"SELECT * FROM results AS t"
                   f"WHERE t.user_id = {user_id}"
                   f"AND t.publish_date = {publish_date}"
                   f"AND t.key_word = {key_word}")
    rows = cursor.fetchall()
    return [Purchase(
        user_id = row[0],
        key_word = row[1],
        publish_date = row[2],
        finish_date = row[3],
        number_of_purchase = row[4],
        subject_of_purchase = row[5],
        price = row[6],
        link = row[7],
        customer = row[8],
        location = row[9]
    ) for row in rows]
