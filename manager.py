import sqlite3
import os

MGMT_DB_PATH = "data/management.db"

def init_mgmt_db():
    if not os.path.exists("data"): os.makedirs("data")
    conn = sqlite3.connect(MGMT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS databases 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, db_name TEXT UNIQUE, file_path TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_permissions 
                      (username TEXT, db_name TEXT, PRIMARY KEY (username, db_name))''')
    conn.commit()
    conn.close()

def get_all_users():
    return ["admin", "sales_manager", "analyst"]

def get_all_databases_metadata():
    conn = sqlite3.connect(MGMT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT db_name FROM databases")
    dbs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return dbs

def add_database_to_mgmt(db_name, file_path, username):
    conn = sqlite3.connect(MGMT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO databases (db_name, file_path) VALUES (?, ?)", (db_name, file_path))
    cursor.execute("INSERT OR IGNORE INTO user_permissions (username, db_name) VALUES (?, ?)", (username, db_name))
    conn.commit()
    conn.close()

def get_allowed_databases(username):
    conn = sqlite3.connect(MGMT_DB_PATH)
    cursor = conn.cursor()
    if username == "admin":
        cursor.execute("SELECT db_name, file_path FROM databases")
    else:
        cursor.execute("SELECT d.db_name, d.file_path FROM databases d JOIN user_permissions p ON d.db_name = p.db_name WHERE p.username = ?", (username,))
    data = {row[0]: f"sqlite:///{row[1]}" for row in cursor.fetchall()}
    conn.close()
    return data

def update_user_permissions(username, selected_dbs):
    conn = sqlite3.connect(MGMT_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_permissions WHERE username = ?", (username,))
    for db_name in selected_dbs:
        cursor.execute("INSERT INTO user_permissions (username, db_name) VALUES (?, ?)", (username, db_name))
    conn.commit()
    conn.close()