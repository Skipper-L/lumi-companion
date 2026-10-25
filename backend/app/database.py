import json
import os
import sqlite3
import ssl
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from uuid import uuid4

from dotenv import load_dotenv

try:
    import pg8000.dbapi as pg8000
except ImportError:  # 本地仍可在未安装 PostgreSQL 驱动时使用 SQLite。
    pg8000 = None


BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / ".env")
DATABASE_PATH = BACKEND_ROOT / "lumi.db"
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def using_postgres():
    return DATABASE_URL.startswith(("postgres://", "postgresql://"))


def get_postgres_ssl_context(parsed_url):
    """按 PostgreSQL URL 的 sslmode 建立连接加密设置。

    Supabase 提供的连接串通常带 ``sslmode=require``：它要求传输加密，
    但不要求客户端额外校验证书链。这兼容部分 Windows 网络环境的自签名
    代理证书。未声明该模式时仍采用严格的系统证书校验。
    """
    verify_setting = os.getenv("DATABASE_SSL_VERIFY", "").strip().lower()
    if verify_setting in {"0", "false", "no"}:
        return ssl._create_unverified_context()

    ssl_mode = parse_qs(parsed_url.query).get("sslmode", [""])[0].lower()
    if ssl_mode == "disable":
        return None
    if ssl_mode in {"require", "allow", "prefer"}:
        return ssl._create_unverified_context()
    return ssl.create_default_context()


class PostgresCursor:
    """将现有 SQLite 风格的 ? 占位符平滑适配为 PostgreSQL。"""

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        statement = query.replace("?", "%s")
        if "INSERT OR IGNORE INTO" in statement.upper():
            statement = statement.replace("INSERT OR IGNORE INTO", "INSERT INTO", 1)
            statement = statement.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"
        self._cursor.execute(statement, () if params is None else params)
        return self

    def _as_dict(self, row):
        """让 pg8000 返回的元组与 sqlite3.Row 一样可按列名读取。"""
        if row is None or isinstance(row, dict):
            return row
        columns = [column[0] for column in (self._cursor.description or [])]
        return dict(zip(columns, row))

    def fetchone(self):
        return self._as_dict(self._cursor.fetchone())

    def fetchall(self):
        return [self._as_dict(row) for row in self._cursor.fetchall()]

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class PostgresConnection:
    """提供与 sqlite3 足够接近的连接接口，减少业务层改动。"""

    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return PostgresCursor(self._connection.cursor())

    def execute(self, query, params=None):
        cursor = self.cursor()
        return cursor.execute(query, params)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


def get_connection():
    if using_postgres():
        if pg8000 is None:
            raise RuntimeError(
                "检测到 DATABASE_URL，但未安装 pg8000。请执行 pip install -r requirements.txt。"
            )
        parsed_url = urlparse(DATABASE_URL)
        if not parsed_url.hostname or not parsed_url.username:
            raise RuntimeError("DATABASE_URL 格式不正确，请重新复制 Supabase 的连接地址。")
        connection = pg8000.connect(
            user=unquote(parsed_url.username),
            password=unquote(parsed_url.password or ""),
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            database=parsed_url.path.lstrip("/") or "postgres",
            ssl_context=get_postgres_ssl_context(parsed_url),
        )
        return PostgresConnection(connection)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def get_now():
    return datetime.now().isoformat(timespec="seconds")


def get_today():
    return datetime.now().date().isoformat()


def add_column_if_not_exists(cursor, table_name, column_name, column_definition):
    if using_postgres():
        cursor.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = ?
            """,
            (table_name,),
        )
        columns = [column["column_name"] for column in cursor.fetchall()]
        if column_name not in columns:
            cursor.execute(
                f"ALTER TABLE {table_name} "
                f"ADD COLUMN {column_name} {column_definition}"
            )
        return

    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column["name"] for column in cursor.fetchall()]

    if column_name not in columns:
        cursor.execute(
            f"ALTER TABLE {table_name} "
            f"ADD COLUMN {column_name} {column_definition}"
        )


POSTGRES_SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id BIGSERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT,
        password_hash TEXT,
        created_at TEXT NOT NULL
    )
    """,
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)",
    """
    CREATE TABLE IF NOT EXISTS conversations (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id),
        character_id TEXT NOT NULL,
        title TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS messages (
        id BIGSERIAL PRIMARY KEY,
        conversation_id BIGINT NOT NULL REFERENCES conversations(id),
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS memberships (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id),
        plan_name TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'inactive',
        started_at TEXT,
        expires_at TEXT,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS custom_characters (
        id TEXT PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id),
        name TEXT NOT NULL,
        avatar TEXT NOT NULL,
        color TEXT NOT NULL,
        atmosphere TEXT NOT NULL,
        speaking_style TEXT NOT NULL,
        relationship TEXT NOT NULL,
        opening TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        gender TEXT NOT NULL DEFAULT 'male',
        background_image TEXT NOT NULL DEFAULT '',
        greeting_image TEXT NOT NULL DEFAULT '',
        boundaries TEXT NOT NULL DEFAULT '',
        memory TEXT NOT NULL DEFAULT '',
        memory_cards TEXT NOT NULL DEFAULT '[]',
        personality_tags TEXT NOT NULL DEFAULT '[]',
        visibility TEXT NOT NULL DEFAULT 'private',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        CHECK (visibility IN ('public', 'private')),
        CHECK (gender IN ('male', 'female'))
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_custom_characters_user_id ON custom_characters(user_id, created_at DESC)",
    "CREATE INDEX IF NOT EXISTS idx_custom_characters_visibility ON custom_characters(visibility, created_at DESC)",
    """
    CREATE TABLE IF NOT EXISTS character_favorites (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id),
        character_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE (user_id, character_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS login_activity (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id),
        login_date TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE (user_id, login_date)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS diary_entries (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT NOT NULL REFERENCES users(id),
        diary_date TEXT NOT NULL,
        content TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE (user_id, diary_date)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_diary_entries_user_date ON diary_entries(user_id, diary_date DESC)",
]


def init_postgres_database():
    connection = get_connection()
    cursor = connection.cursor()
    try:
        for statement in POSTGRES_SCHEMA_STATEMENTS:
            cursor.execute(statement)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    print("PostgreSQL 数据库已准备完成。")


def init_database():
    if using_postgres():
        init_postgres_database()
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT,
            password_hash TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    add_column_if_not_exists(cursor, "users", "email", "TEXT")
    add_column_if_not_exists(cursor, "users", "password_hash", "TEXT")

    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username
        ON users(username)
        """
    )
    cursor.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email
        ON users(email)
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            character_id TEXT NOT NULL,
            title TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS memberships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'inactive',
            started_at TEXT,
            expires_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS custom_characters (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            avatar TEXT NOT NULL,
            color TEXT NOT NULL,
            atmosphere TEXT NOT NULL,
            speaking_style TEXT NOT NULL,
            relationship TEXT NOT NULL,
            opening TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            gender TEXT NOT NULL DEFAULT 'male',
            background_image TEXT NOT NULL DEFAULT '',
            greeting_image TEXT NOT NULL DEFAULT '',
            boundaries TEXT NOT NULL DEFAULT '',
            memory TEXT NOT NULL DEFAULT '',
            memory_cards TEXT NOT NULL DEFAULT '[]',
            personality_tags TEXT NOT NULL DEFAULT '[]',
            visibility TEXT NOT NULL DEFAULT 'private',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            CHECK (visibility IN ('public', 'private')),
            CHECK (gender IN ('male', 'female'))
        )
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_custom_characters_user_id
        ON custom_characters(user_id, created_at DESC)
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_custom_characters_visibility
        ON custom_characters(visibility, created_at DESC)
        """
    )

    # 兼容已有数据库：旧角色会自动获得默认性别与空背景图。
    add_column_if_not_exists(
        cursor,
        "custom_characters",
        "description",
        "TEXT NOT NULL DEFAULT ''",
    )
    add_column_if_not_exists(
        cursor,
        "custom_characters",
        "gender",
        "TEXT NOT NULL DEFAULT 'male'",
    )
    add_column_if_not_exists(
        cursor,
        "custom_characters",
        "background_image",
        "TEXT NOT NULL DEFAULT ''",
    )
    add_column_if_not_exists(
        cursor,
        "custom_characters",
        "greeting_image",
        "TEXT NOT NULL DEFAULT ''",
    )
    add_column_if_not_exists(
        cursor,
        "custom_characters",
        "memory_cards",
        "TEXT NOT NULL DEFAULT '[]'",
    )
    add_column_if_not_exists(
        cursor,
        "custom_characters",
        "personality_tags",
        "TEXT NOT NULL DEFAULT '[]'",
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS character_favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            character_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (user_id, character_id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS login_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            login_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (user_id, login_date)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS diary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            diary_date TEXT NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE (user_id, diary_date)
        )
        """
    )
    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_diary_entries_user_date
        ON diary_entries(user_id, diary_date DESC)
        """
    )

    connection.commit()
    connection.close()

    print(f"数据库已准备完成：{DATABASE_PATH}")
    print("用户、聊天、角色、收藏、登录记录数据表已准备完成。")


# =========================
# 用户
# =========================

def create_user(username: str, email: str, password_hash: str):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        if using_postgres():
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                RETURNING id
                """,
                (username, email, password_hash, get_now()),
            )
            user_id = cursor.fetchone()["id"]
        else:
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (username, email, password_hash, get_now()),
            )
            user_id = cursor.lastrowid
        connection.commit()
        return {"id": user_id, "username": username, "email": email}
    except Exception as error:
        integrity_error = (
            isinstance(error, sqlite3.IntegrityError)
            or getattr(error, "sqlstate", None) == "23505"
            or error.__class__.__name__ == "IntegrityError"
        )
        if not integrity_error:
            raise
        connection.rollback()
        return None
    finally:
        connection.close()


def get_user_by_username(username: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, username, email, password_hash, created_at
        FROM users
        WHERE username = ?
        """,
        (username,),
    )
    user = cursor.fetchone()
    connection.close()
    return dict(user) if user else None


def get_user_by_id(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, username, email, created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    )
    user = cursor.fetchone()
    connection.close()
    return dict(user) if user else None


# =========================
# 每日登录记录
# =========================

def record_daily_login(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO login_activity (user_id, login_date, created_at)
        VALUES (?, ?, ?)
        """,
        (user_id, get_today(), get_now()),
    )
    connection.commit()
    connection.close()


def get_login_day_count(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM login_activity
        WHERE user_id = ?
        """,
        (user_id,),
    )
    total = cursor.fetchone()["total"]
    connection.close()
    return total


# =========================
# 聊天记录
# =========================

def save_chat_turn(user_id: int, character_id: str, user_content: str, assistant_content: str):
    connection = get_connection()
    cursor = connection.cursor()
    now = get_now()

    cursor.execute(
        """
        SELECT id
        FROM conversations
        WHERE user_id = ? AND character_id = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (user_id, character_id),
    )
    conversation = cursor.fetchone()

    if conversation is None:
        if using_postgres():
            cursor.execute(
                """
                INSERT INTO conversations (user_id, character_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                RETURNING id
                """,
                (user_id, character_id, "与角色的聊天", now, now),
            )
            conversation_id = cursor.fetchone()["id"]
        else:
            cursor.execute(
                """
                INSERT INTO conversations (user_id, character_id, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, character_id, "与角色的聊天", now, now),
            )
            conversation_id = cursor.lastrowid
    else:
        conversation_id = conversation["id"]

    cursor.execute(
        """
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (conversation_id, "user", user_content, now),
    )
    cursor.execute(
        """
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (conversation_id, "assistant", assistant_content, get_now()),
    )
    cursor.execute(
        """
        UPDATE conversations
        SET updated_at = ?
        WHERE id = ?
        """,
        (get_now(), conversation_id),
    )
    connection.commit()
    connection.close()
    return conversation_id


def get_chat_history(user_id: int, character_id: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT messages.id, messages.role, messages.content, messages.created_at
        FROM messages
        JOIN conversations ON messages.conversation_id = conversations.id
        WHERE conversations.user_id = ? AND conversations.character_id = ?
        ORDER BY messages.id ASC
        """,
        (user_id, character_id),
    )
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def delete_chat_history(user_id: int, character_id: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        DELETE FROM messages
        WHERE conversation_id IN (
            SELECT id FROM conversations WHERE user_id = ? AND character_id = ?
        )
        """,
        (user_id, character_id),
    )
    deleted_message_count = cursor.rowcount
    cursor.execute(
        """
        DELETE FROM conversations
        WHERE user_id = ? AND character_id = ?
        """,
        (user_id, character_id),
    )
    connection.commit()
    connection.close()
    return deleted_message_count


def get_chat_character_count(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT COUNT(DISTINCT character_id) AS total
        FROM conversations
        WHERE user_id = ?
        """,
        (user_id,),
    )
    total = cursor.fetchone()["total"]
    connection.close()
    return total


# =========================
# 自建角色
# =========================

def custom_character_to_dict(row):
    character = dict(row)
    try:
        memory_cards = json.loads(character.get("memory_cards") or "[]")
    except (TypeError, json.JSONDecodeError):
        memory_cards = []
    character["memory_cards"] = [
        card for card in memory_cards
        if isinstance(card, dict) and card.get("key") and card.get("content")
    ]
    if not character["memory_cards"] and character.get("memory", "").strip():
        character["memory_cards"] = [{
            "id": "legacy-memory",
            "key": "初始记忆",
            "content": character["memory"].strip(),
        }]
    try:
        personality_tags = json.loads(character.get("personality_tags") or "[]")
    except (TypeError, json.JSONDecodeError):
        personality_tags = []
    character["personality_tags"] = [
        tag.strip() for tag in personality_tags
        if isinstance(tag, str) and tag.strip()
    ]
    character["description"] = (
        character.get("description", "").strip()
        or character.get("opening", "").strip()
    )
    character["gender"] = (
        character.get("gender")
        if character.get("gender") in {"male", "female"}
        else "male"
    )
    character["background_image"] = character.get("background_image", "")
    character["greeting_image"] = character.get("greeting_image", "")
    character["subtitle"] = character["relationship"]
    character["category"] = "自定义"
    character["tags"] = list(dict.fromkeys([
        *character["personality_tags"],
        character["atmosphere"],
        character["speaking_style"],
    ]))
    character["message"] = character["description"]
    character["status"] = "正在等待你的消息"
    character["online"] = True
    return character


def create_custom_character(user_id: int, data: dict):
    connection = get_connection()
    cursor = connection.cursor()
    now = get_now()
    character_id = f"custom_{uuid4().hex}"

    name = data["name"].strip()
    avatar = data.get("avatar", "").strip() or name[:1] or "陪"
    gender = data.get("gender", "male")
    if gender not in {"male", "female"}:
        gender = "male"

    cursor.execute(
        """
        INSERT INTO custom_characters (
            id, user_id, name, avatar, color, atmosphere, speaking_style,
            relationship, opening, description, gender, background_image,
            greeting_image,
            boundaries, memory, memory_cards, personality_tags, visibility, created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            character_id,
            user_id,
            name,
            avatar,
            data.get("color", "purple"),
            data.get("atmosphere", "专属陪伴"),
            data.get("speaking_style", "专属陪伴"),
            data.get("relationship", "知心朋友"),
            data.get("opening", f"你好呀，我是{name}，很高兴认识你。"),
            data.get("description", ""),
            gender,
            data.get("background_image", ""),
            data.get("greeting_image", ""),
            data.get("boundaries", ""),
            data.get("memory", ""),
            json.dumps(data.get("memory_cards", []), ensure_ascii=False),
            json.dumps(data.get("personality_tags", []), ensure_ascii=False),
            data.get("visibility", "private"),
            now,
            now,
        ),
    )
    connection.commit()

    cursor.execute(
        """
        SELECT custom_characters.*, users.username AS owner_username
        FROM custom_characters
        JOIN users ON users.id = custom_characters.user_id
        WHERE custom_characters.id = ?
        """,
        (character_id,),
    )
    character = custom_character_to_dict(cursor.fetchone())
    connection.close()
    return character


def get_public_custom_characters():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT custom_characters.*, users.username AS owner_username
        FROM custom_characters
        JOIN users ON users.id = custom_characters.user_id
        WHERE custom_characters.visibility = 'public'
        ORDER BY custom_characters.created_at DESC
        """
    )
    characters = [custom_character_to_dict(row) for row in cursor.fetchall()]
    connection.close()
    return characters


def get_my_custom_characters(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT custom_characters.*, users.username AS owner_username
        FROM custom_characters
        JOIN users ON users.id = custom_characters.user_id
        WHERE custom_characters.user_id = ?
        ORDER BY custom_characters.created_at DESC
        """,
        (user_id,),
    )
    characters = [custom_character_to_dict(row) for row in cursor.fetchall()]
    connection.close()
    return characters


def get_custom_character_for_chat(user_id: int, character_id: str):
    """读取本人角色或公开角色，绝不泄露他人的私有设定。"""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT custom_characters.*, users.username AS owner_username
        FROM custom_characters
        JOIN users ON users.id = custom_characters.user_id
        WHERE custom_characters.id = ?
          AND (custom_characters.user_id = ? OR custom_characters.visibility = 'public')
        LIMIT 1
        """,
        (character_id, user_id),
    )
    row = cursor.fetchone()
    connection.close()
    return custom_character_to_dict(row) if row else None


def delete_custom_character(user_id: int, character_id: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT 1 FROM custom_characters WHERE id = ? AND user_id = ?",
        (character_id, user_id),
    )
    if cursor.fetchone() is None:
        connection.close()
        return {
            "deleted_count": 0,
            "deleted_message_count": 0,
            "deleted_conversation_count": 0,
        }
    # 删除角色时同步清理当前账号与该角色的消息、会话和收藏，
    # 避免会话记录页继续显示“已删除的角色”。
    cursor.execute(
        """
        DELETE FROM messages
        WHERE conversation_id IN (
            SELECT id FROM conversations WHERE user_id = ? AND character_id = ?
        )
        """,
        (user_id, character_id),
    )
    deleted_message_count = cursor.rowcount
    cursor.execute(
        """
        DELETE FROM conversations
        WHERE user_id = ? AND character_id = ?
        """,
        (user_id, character_id),
    )
    deleted_conversation_count = cursor.rowcount
    cursor.execute(
        """
        DELETE FROM character_favorites
        WHERE user_id = ? AND character_id = ?
        """,
        (user_id, character_id),
    )
    cursor.execute(
        """
        DELETE FROM custom_characters
        WHERE id = ? AND user_id = ?
        """,
        (character_id, user_id),
    )
    deleted_count = cursor.rowcount
    connection.commit()
    connection.close()
    return {
        "deleted_count": deleted_count,
        "deleted_message_count": deleted_message_count,
        "deleted_conversation_count": deleted_conversation_count,
    }


def update_custom_character_memory_cards(
    user_id: int,
    character_id: str,
    memory_cards: list[dict],
):
    """仅允许创建者更新其自建角色的记忆卡。"""
    connection = get_connection()
    cursor = connection.cursor()
    normalized_cards = [
        {
            "id": str(card.get("id") or uuid4().hex),
            "key": str(card.get("key") or "").strip(),
            "content": str(card.get("content") or "").strip(),
        }
        for card in memory_cards
    ]
    normalized_cards = [
        card for card in normalized_cards if card["key"] and card["content"]
    ]
    memory_summary = "\n".join(
        f"{card['key']}：{card['content']}" for card in normalized_cards
    )[:240]

    cursor.execute(
        """
        UPDATE custom_characters
        SET memory_cards = ?, memory = ?, updated_at = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            json.dumps(normalized_cards, ensure_ascii=False),
            memory_summary,
            get_now(),
            character_id,
            user_id,
        ),
    )
    if cursor.rowcount == 0:
        connection.close()
        return None

    connection.commit()
    cursor.execute(
        """
        SELECT custom_characters.*, users.username AS owner_username
        FROM custom_characters
        JOIN users ON users.id = custom_characters.user_id
        WHERE custom_characters.id = ? AND custom_characters.user_id = ?
        """,
        (character_id, user_id),
    )
    character = custom_character_to_dict(cursor.fetchone())
    connection.close()
    return character


# =========================
# 收藏
# =========================

def add_favorite(user_id: int, character_id: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT OR IGNORE INTO character_favorites (user_id, character_id, created_at)
        VALUES (?, ?, ?)
        """,
        (user_id, character_id, get_now()),
    )
    connection.commit()
    connection.close()


def remove_favorite(user_id: int, character_id: str):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        DELETE FROM character_favorites
        WHERE user_id = ? AND character_id = ?
        """,
        (user_id, character_id),
    )
    deleted_count = cursor.rowcount
    connection.commit()
    connection.close()
    return deleted_count


def get_favorite_character_ids(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT character_id
        FROM character_favorites
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,),
    )
    character_ids = [row["character_id"] for row in cursor.fetchall()]
    connection.close()
    return character_ids


def get_favorite_count(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT COUNT(*) AS total
        FROM character_favorites
        WHERE user_id = ?
        """,
        (user_id,),
    )
    total = cursor.fetchone()["total"]
    connection.close()
    return total


# =========================
# 我的空间统计
# =========================

def get_profile_summary(user_id: int):
    return {
        "chat_character_count": get_chat_character_count(user_id),
        "favorite_count": get_favorite_count(user_id),
        "login_day_count": get_login_day_count(user_id),
    }


def save_diary_entry(user_id: int, diary_date: str, content: str):
    connection = get_connection()
    now = get_now()
    connection.execute(
        """
        INSERT INTO diary_entries
            (user_id, diary_date, content, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id, diary_date) DO UPDATE SET
            content = excluded.content,
            updated_at = excluded.updated_at
        """,
        (user_id, diary_date, content, now, now),
    )
    connection.commit()
    row = connection.execute(
        """
        SELECT id, diary_date, content, created_at, updated_at
        FROM diary_entries
        WHERE user_id = ? AND diary_date = ?
        """,
        (user_id, diary_date),
    ).fetchone()
    connection.close()
    return dict(row)


def get_diary_entries(user_id: int):
    connection = get_connection()
    rows = connection.execute(
        """
        SELECT id, diary_date, content, created_at, updated_at
        FROM diary_entries
        WHERE user_id = ?
        ORDER BY diary_date DESC
        """,
        (user_id,),
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_conversation_records(user_id: int):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            conversations.id AS conversation_id,
            conversations.character_id,
            conversations.updated_at,
            (
                SELECT messages.content
                FROM messages
                WHERE messages.conversation_id = conversations.id
                ORDER BY messages.id DESC
                LIMIT 1
            ) AS last_message,
            (
                SELECT COUNT(*)
                FROM messages
                WHERE messages.conversation_id = conversations.id
            ) AS message_count
        FROM conversations
        WHERE conversations.user_id = ?
        ORDER BY conversations.updated_at DESC
        """,
        (user_id,),
    )
    records = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return records
