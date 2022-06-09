CREATE TABLE users (
chat_id INTEGER NOT NULL UNIQUE,
current_cartoon_number INTEGER,
last_cartoon_number INTEGER,
send_trends INTEGER NOT NULL DEFAULT 1,
send_notifications INTEGER NOT NULL DEFAULT 1,
time_to_trends TEXT NOT NULL DEFAULT '12.00',
time_to_notifications TEXT NOT NULL DEFAULT '12.00'
);


