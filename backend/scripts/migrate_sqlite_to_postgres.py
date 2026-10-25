"""将 Lumi 的本地 SQLite 数据安全复制到 PostgreSQL。

默认只做预检查。只有显式传入 --confirm 才会写入远程数据库；
脚本不会修改、删除或覆盖本地 lumi.db。
"""

import argparse
import sqlite3
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

from app.database import get_connection, init_database, using_postgres  # noqa: E402


TABLES = [
    "users",
    "conversations",
    "messages",
    "memberships",
    "custom_characters",
    "character_favorites",
    "login_activity",
    "diary_entries",
]

SEQUENCE_TABLES = [
    "users",
    "conversations",
    "messages",
    "memberships",
    "character_favorites",
    "login_activity",
    "diary_entries",
]


def read_sqlite_counts(connection):
    return {
        table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        for table in TABLES
    }


def read_postgres_counts(connection):
    cursor = connection.cursor()
    counts = {}
    for table in TABLES:
        cursor.execute(f"SELECT COUNT(*) AS total FROM {table}")
        counts[table] = cursor.fetchone()["total"]
    return counts


def format_counts(counts):
    return "， ".join(f"{table}：{count}" for table, count in counts.items())


def migrate_table(source, target, table):
    rows = source.execute(f"SELECT * FROM {table}").fetchall()
    if not rows:
        return 0

    columns = [
        column[0]
        for column in source.execute(f"SELECT * FROM {table} LIMIT 0").description
    ]
    placeholders = ", ".join("?" for _ in columns)
    column_names = ", ".join(columns)
    cursor = target.cursor()

    for row in rows:
        cursor.execute(
            f"INSERT INTO {table} ({column_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING",
            tuple(row[column] for column in columns),
        )
    return len(rows)


def reset_sequences(target):
    cursor = target.cursor()
    for table in SEQUENCE_TABLES:
        cursor.execute(
            """
            SELECT setval(
                pg_get_serial_sequence(?, 'id'),
                COALESCE((SELECT MAX(id) FROM """ + table + """), 1),
                true
            )
            """,
            (table,),
        )


def main():
    parser = argparse.ArgumentParser(description="迁移 Lumi SQLite 数据到 PostgreSQL")
    parser.add_argument(
        "--sqlite-path",
        default=str(BACKEND_ROOT / "lumi.db"),
        help="源 SQLite 数据库路径，默认是 backend/lumi.db",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="确认写入远程 PostgreSQL；不传此参数只做预检查",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="允许远程数据库已有数据时继续，通常不需要使用",
    )
    args = parser.parse_args()

    source_path = Path(args.sqlite_path).resolve()
    if not source_path.exists():
        raise SystemExit(f"找不到本地 SQLite 文件：{source_path}")
    if not using_postgres():
        raise SystemExit("未检测到 PostgreSQL DATABASE_URL，请检查 backend/.env。")

    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row
    source_counts = read_sqlite_counts(source)

    print("本地 SQLite 数据：", format_counts(source_counts))
    if not args.confirm:
        print("这是预检查，尚未写入远程数据库。确认迁移时请加 --confirm。")
        source.close()
        return

    init_database()
    target = get_connection()
    target_counts = read_postgres_counts(target)
    print("远程 PostgreSQL 当前数据：", format_counts(target_counts))

    if any(target_counts.values()) and not args.allow_existing:
        target.close()
        source.close()
        raise SystemExit(
            "远程数据库已有数据，为防止混入或覆盖，本次迁移已停止。"
            "确认目标库为空后再执行；不要轻易使用 --allow-existing。"
        )

    try:
        migrated = {table: migrate_table(source, target, table) for table in TABLES}
        reset_sequences(target)
        target.commit()
    except Exception:
        target.rollback()
        raise
    finally:
        target.close()
        source.close()

    print("迁移完成：", format_counts(migrated))
    print("本地 lumi.db 未被修改。请先验证远程数据，再继续部署。")


if __name__ == "__main__":
    main()
