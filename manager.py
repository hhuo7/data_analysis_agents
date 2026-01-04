import sqlite3
import os

# 管理数据库路径，存储用户信息和权限
MGMT_DB = "management.db"

def init_mgmt_db():
    """
    初始化管理系统：创建用户表、数据库表和权限关联表 。
    符合 Assignment 要求：能够限制特定用户访问特定数据库。
    """
    conn = sqlite3.connect(MGMT_DB)
    cursor = conn.cursor()

    # 1. 创建用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            role TEXT DEFAULT 'user'
        )
    """)

    # 2. 创建数据库列表 (用于快速集成新库 )
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS databases (
            db_id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE,
            file_path TEXT
        )
    """)

    # 3. 权限表：定义用户与数据库的映射 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS permissions (
            username TEXT,
            db_nickname TEXT,
            FOREIGN KEY(username) REFERENCES users(username),
            FOREIGN KEY(db_nickname) REFERENCES databases(nickname)
        )
    """)

    # 初始化演示数据
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES ('admin', 'admin')")
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES ('analyst', 'user')")
    cursor.execute("INSERT OR IGNORE INTO users (username, role) VALUES ('manager', 'user')")  

    conn.commit()
    conn.close()

def add_database_to_mgmt(nickname, file_path, owner):
    """
    便捷集成逻辑 ：
    将新的 .sqlite 文件路径存入管理系统，并默认赋予上传者权限。
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
    实现用户限制 ：
    根据当前登录角色，仅返回其有权访问的数据库路径字典。
    """
    conn = sqlite3.connect(MGMT_DB)
    cursor = conn.cursor()
    
    # 如果是 admin，返回所有库；否则按权限表过滤
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
    更新用户权限，由 Admin 在后台操作。
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