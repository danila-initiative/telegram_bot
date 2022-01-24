CREATE TABLE if NOT EXISTS search_query(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    search_string VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    min_price INTEGER NULL,
    max_price INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT (datetime('now','localtime')),
    FOREIGN KEY (user_id) REFERENCES user (user_id)
);
