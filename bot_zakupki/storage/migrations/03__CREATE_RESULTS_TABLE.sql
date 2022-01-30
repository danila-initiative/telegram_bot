CREATE TABLE IF NOT EXISTS result(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publish_date TIMESTAMP NOT NULL,
    finish_date TIMESTAMP NOT NULL,
    number_of_purchase VARCHAR(255) NOT NULL,
    subject_of_purchase VARCHAR(750) NULL,
    price INTEGER NOT NULL,
    link VARCHAR(500) NOT NULL,
    customer VARCHAR(500) NOT NULL,
    query_id INTEGER NOT NULL,
    FOREIGN KEY (query_id) REFERENCES search_query (id)
);
