import sqlite3
import json
from pathlib import Path

DB_PATH = "perf_dashboard.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product     TEXT NOT NULL,
            version     TEXT NOT NULL,
            config      TEXT NOT NULL,
            data_size   INTEGER NOT NULL,
            threads     INTEGER NOT NULL,
            tps         REAL NOT NULL,
            response_sec REAL NOT NULL,
            error_pct   REAL NOT NULL,
            cpu_avg     REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def is_empty():
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) as cnt FROM measurements").fetchone()
    conn.close()
    return row["cnt"] == 0


def load_sample_data():
    sample_path = Path("sample_data/sample.json")
    if not sample_path.exists():
        return
    data = json.loads(sample_path.read_text(encoding="utf-8"))
    conn = get_conn()
    conn.executemany("""
        INSERT INTO measurements (product, version, config, data_size, threads, tps, response_sec, error_pct, cpu_avg)
        VALUES (:product, :version, :config, :data_size, :threads, :tps, :response_sec, :error_pct, :cpu_avg)
    """, data)
    conn.commit()
    conn.close()


def get_products():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT product FROM measurements ORDER BY product").fetchall()
    conn.close()
    return [r["product"] for r in rows]


def get_versions(product: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT version FROM measurements WHERE product=? ORDER BY version",
        (product,)
    ).fetchall()
    conn.close()
    return [r["version"] for r in rows]


def get_configs(product: str):
    conn = get_conn()
    rows = conn.execute(
        "SELECT DISTINCT config FROM measurements WHERE product=? ORDER BY config",
        (product,)
    ).fetchall()
    conn.close()
    return [r["config"] for r in rows]


def get_measurements(product: str, version: str = None):
    conn = get_conn()
    if version:
        rows = conn.execute(
            "SELECT * FROM measurements WHERE product=? AND version=? ORDER BY config, data_size",
            (product, version)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM measurements WHERE product=? ORDER BY version, config, data_size",
            (product,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_measurements(data: list):
    conn = get_conn()
    conn.executemany("""
        INSERT INTO measurements (product, version, config, data_size, threads, tps, response_sec, error_pct, cpu_avg)
        VALUES (:product, :version, :config, :data_size, :threads, :tps, :response_sec, :error_pct, :cpu_avg)
    """, data)
    conn.commit()
    conn.close()
