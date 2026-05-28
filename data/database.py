# data/database.py
import sqlite3

DB_PATH = "data/users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT,
        diet       TEXT DEFAULT 'omnivore',
        goal       TEXT DEFAULT 'none',
        allergies  TEXT DEFAULT '',
        servings   INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS history (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER REFERENCES users(id),
        recipe_id   TEXT,
        recipe_name TEXT,
        eaten_at    TEXT DEFAULT CURRENT_TIMESTAMP,
        saved       INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS fridge (
        id       INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id  INTEGER REFERENCES users(id),
        name     TEXT,
        quantity TEXT,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP
    );

    INSERT OR IGNORE INTO users (id, name, diet, goal, allergies, servings)
    VALUES (1, '預設使用者', 'omnivore', 'none', '', 1);
    """)

    conn.commit()
    conn.close()
    print("✅ 資料庫初始化完成")