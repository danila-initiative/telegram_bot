CREATE TABLE if NOT EXISTS search_query(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    search_string VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    min_price INTEGER DEFAULT 0,
    max_price INTEGER NULL,
    created_at TIMESTAMP DEFAULT (datetime('now','localtime')),
    subscription_last_day TIMESTAMP DEFAULT (datetime('now', '+7 days','localtime')),
    payment_last_day TIMESTAMP DEFAULT (datetime('now','localtime')),
    deleted INTEGER DEFAULT 0
);
