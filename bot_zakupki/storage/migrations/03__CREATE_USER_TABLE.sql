CREATE TABLE IF NOT EXISTS user(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    first_bot_start_date TIMESTAMP DEFAULT (datetime('now','localtime')),
    bot_start_date TIMESTAMP DEFAULT (datetime('now','localtime')),
    bot_is_active INTEGER DEFAULT 1,
    trial_start_date TIMESTAMP DEFAULT NULL,
    trial_end_date TIMESTAMP DEFAULT NULL,
    number_of_sending INTEGER DEFAULT 0,
    downtime_notification INTEGER DEFAULT 0
);