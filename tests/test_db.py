import os
import sqlite3
import pytest


# TODO: автоматиизировать создание таблиц
# выполнить все файлы из папки bot_zakupki/storage/migrations по примеру функции ниже
@pytest.fixture(scope='function')
def db(tmpdir):
    file = os.path.join(tmpdir.strpath, "test.storage")
    conn = sqlite3.connect(file)
    conn.execute("CREATE TABLE blog (id, title, text)")
    yield conn
    conn.close()


def test_entry_creation(db):
    query = ("INSERT INTO blog "
             "(id, title, text)"
             "VALUES (?, ?, ?)")

    values = (1,
              "PyTest",
              "This is a blog entry")

    db.execute(query, values)