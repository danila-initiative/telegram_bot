CREATE TABLE IF NOT EXISTS user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL, -- telegram_id
    first_bot_start_date TIMESTAMP DEFAULT (datetime('now','localtime')),
    bot_start_date TIMESTAMP DEFAULT (datetime('now','localtime')),
    bot_is_active INTEGER DEFAULT 1,
    max_number_of_queries INTEGER DEFAULT 0,
    subscription_last_day TIMESTAMP DEFAULT NULL,
    payment_last_day TIMESTAMP DEFAULT NULL
);