import sqlite3
import os


MGMT_DB = "management.db"

def init_mgmt_db():
    """
    Initialize the management system: create user table, database table, and permission association table.
    """
    conn = sqlite3.connect(MGMT_DB)
    cursor = conn.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            role TEXT DEFAULT 'user'
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS databases (
            db_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE,
            file_path TEXT
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            username TEXT,
            db_nickname TEXT,
            FOREIGN KEY(username) REFERENCES users(username),
            FOREIGN KEY(db_nickname) REFERENCES databases(nickname)
        )
    """)


    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES ('admin', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES ('analyst', 'user')")
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES ('manager', 'user')")  

    conn.commit()
    conn.close()

def add_database_to_mgmt(nickname, file_path, owner):
    """
    Save the new .sqlite file path into the management system and grant permission to the uploader by default.
    """
    conn = sqlite3.connect(MGMT_DB)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO databases (nickname, file_path) VALUES (?, ?)", (nickname, file_path))
        cursor.execute("INSERT INTO permissions (username, db_nickname) VALUES (?, ?)", (owner, nickname))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def get_allowed_databases(username):
    """
    Implement user restrictions:
    Return a dictionary of database paths that the user is authorized to access based on their current role.
    """
    conn = sqlite3.connect(MGMT_DB)
    cursor = conn.cursor()
    

    if username == 'admin':
        cursor.execute("SELECT nickname, file_path FROM databases")
    else:
        cursor.execute("""
            SELECT d.nickname, d.file_path 
            FROM databases d
            JOIN permissions p ON d.nickname = p.db_nickname
            WHERE p.username = ?
        """, (username,))
    
    dbs = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return dbs

def get_all_users():
    conn = sqlite3.connect(MGMT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return users

def update_user_permissions(username, db_nicknames):
    """
    Update user permissions, operated by Admin in the background.
    """
    conn = sqlite3.connect(MGMT_DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM permissions WHERE username = ?", (username,))
    for nick in db_nicknames:
        cursor.execute("INSERT INTO permissions (username, db_nickname) VALUES (?, ?)", (username, nick))
    conn.commit()
    conn.close()

def get_all_databases_metadata():
    conn = sqlite3.connect(MGMT_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nickname FROM databases")
    dbs = [row[0] for row in cursor.fetchall()]
    conn.close()
    return dbs