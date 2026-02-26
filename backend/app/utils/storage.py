from __future__ import annotations

import json
import os
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

EventMap = dict[str, list[dict[str, Any]]]
TABLES = ("intake_events", "dose_checks", "overrides")


def _backend() -> str:
    configured = (os.getenv("CLINIQ_DB_BACKEND") or "").strip().lower()
    if configured in {"postgres", "sqlite"}:
        return configured
    if os.getenv("DATABASE_URL_LOCAL"):
        return "postgres"
    return "sqlite"


def _db_path() -> str:
    env_path = os.getenv("CLINIQ_DB_PATH")
    if env_path:
        return env_path
    base = Path(__file__).resolve().parents[2]
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir / "cliniq_flow.db")


def _sqlite_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _postgres_connect(dsn: str | None = None):
    try:
        import psycopg
        from psycopg.rows import dict_row
    except Exception as exc:  # pragma: no cover - exercised only in postgres mode.
        raise RuntimeError("psycopg is required for Postgres mode") from exc

    url = dsn or os.getenv("DATABASE_URL_LOCAL") or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL_LOCAL or DATABASE_URL is required for Postgres mode")
    return psycopg.connect(url, row_factory=dict_row)


def init_db() -> None:
    if _backend() == "postgres":
        _init_postgres()
    else:
        _init_sqlite()


def _init_postgres() -> None:
    with _postgres_connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intake_events (
                event_id TEXT PRIMARY KEY,
                visit_id TEXT NOT NULL,
                urgency_level TEXT NOT NULL,
                red_flags_json JSONB NOT NULL DEFAULT '[]'::jsonb,
                sync_status TEXT NOT NULL DEFAULT 'pending',
                source_system TEXT NOT NULL DEFAULT 'local',
                last_synced_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dose_checks (
                event_id TEXT PRIMARY KEY,
                visit_id TEXT NOT NULL,
                drug_name TEXT NOT NULL,
                chosen_dose_mg_per_day INTEGER NOT NULL,
                safe BOOLEAN NOT NULL,
                warnings_json JSONB NOT NULL DEFAULT '[]'::jsonb,
                sync_status TEXT NOT NULL DEFAULT 'pending',
                source_system TEXT NOT NULL DEFAULT 'local',
                last_synced_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS overrides (
                event_id TEXT PRIMARY KEY,
                med_order_id TEXT NOT NULL,
                override_reason TEXT NOT NULL,
                actor_role TEXT NOT NULL,
                doctor_id TEXT,
                sync_status TEXT NOT NULL DEFAULT 'pending',
                source_system TEXT NOT NULL DEFAULT 'local',
                last_synced_at TIMESTAMPTZ,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        conn.commit()


def _init_sqlite() -> None:
    with _sqlite_connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intake_events (
                event_id TEXT PRIMARY KEY,
                visit_id TEXT NOT NULL,
                urgency_level TEXT NOT NULL,
                red_flags_json TEXT NOT NULL,
                sync_status TEXT NOT NULL DEFAULT 'pending',
                source_system TEXT NOT NULL DEFAULT 'local',
                last_synced_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dose_checks (
                event_id TEXT PRIMARY KEY,
                visit_id TEXT NOT NULL,
                drug_name TEXT NOT NULL,
                chosen_dose_mg_per_day INTEGER NOT NULL,
                safe INTEGER NOT NULL,
                warnings_json TEXT NOT NULL,
                sync_status TEXT NOT NULL DEFAULT 'pending',
                source_system TEXT NOT NULL DEFAULT 'local',
                last_synced_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS overrides (
                event_id TEXT PRIMARY KEY,
                med_order_id TEXT NOT NULL,
                override_reason TEXT NOT NULL,
                actor_role TEXT NOT NULL,
                doctor_id TEXT,
                sync_status TEXT NOT NULL DEFAULT 'pending',
                source_system TEXT NOT NULL DEFAULT 'local',
                last_synced_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        _ensure_sqlite_columns(conn)


def _ensure_sqlite_columns(conn: sqlite3.Connection) -> None:
    for table, required in {
        "intake_events": {"sync_status": "TEXT DEFAULT 'pending'", "source_system": "TEXT DEFAULT 'local'", "last_synced_at": "TEXT"},
        "dose_checks": {"sync_status": "TEXT DEFAULT 'pending'", "source_system": "TEXT DEFAULT 'local'", "last_synced_at": "TEXT"},
        "overrides": {"sync_status": "TEXT DEFAULT 'pending'", "source_system": "TEXT DEFAULT 'local'", "last_synced_at": "TEXT"},
    }.items():
        existing = {row["name"] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        for col_name, col_def in required.items():
            if col_name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
    conn.commit()


def log_intake(event_id: str, visit_id: str, urgency_level: str, red_flags: list[str]) -> None:
    init_db()
    source_system = os.getenv("SOURCE_SYSTEM", "local")
    if _backend() == "postgres":
        with _postgres_connect() as conn:
            conn.execute(
                """
                INSERT INTO intake_events (event_id, visit_id, urgency_level, red_flags_json, sync_status, source_system)
                VALUES (%s, %s, %s, %s::jsonb, 'pending', %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (event_id, visit_id, urgency_level, json.dumps(red_flags), source_system),
            )
            conn.commit()
        return

    with _sqlite_connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO intake_events (
                event_id, visit_id, urgency_level, red_flags_json, sync_status, source_system
            )
            VALUES (?, ?, ?, ?, 'pending', ?)
            """,
            (event_id, visit_id, urgency_level, json.dumps(red_flags), source_system),
        )
        conn.commit()


def log_dose_check(
    event_id: str,
    visit_id: str,
    drug_name: str,
    chosen_dose_mg_per_day: int,
    safe: bool,
    warnings: list[str],
) -> None:
    init_db()
    source_system = os.getenv("SOURCE_SYSTEM", "local")
    if _backend() == "postgres":
        with _postgres_connect() as conn:
            conn.execute(
                """
                INSERT INTO dose_checks (
                    event_id, visit_id, drug_name, chosen_dose_mg_per_day, safe, warnings_json, sync_status, source_system
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, 'pending', %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (event_id, visit_id, drug_name, chosen_dose_mg_per_day, safe, json.dumps(warnings), source_system),
            )
            conn.commit()
        return

    with _sqlite_connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO dose_checks (
                event_id, visit_id, drug_name, chosen_dose_mg_per_day, safe, warnings_json, sync_status, source_system
            )
            VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (event_id, visit_id, drug_name, chosen_dose_mg_per_day, int(safe), json.dumps(warnings), source_system),
        )
        conn.commit()


def log_override(event_id: str, med_order_id: str, override_reason: str, actor_role: str, doctor_id: str | None) -> None:
    init_db()
    source_system = os.getenv("SOURCE_SYSTEM", "local")
    if _backend() == "postgres":
        with _postgres_connect() as conn:
            conn.execute(
                """
                INSERT INTO overrides (
                    event_id, med_order_id, override_reason, actor_role, doctor_id, sync_status, source_system
                )
                VALUES (%s, %s, %s, %s, %s, 'pending', %s)
                ON CONFLICT (event_id) DO NOTHING
                """,
                (event_id, med_order_id, override_reason, actor_role, doctor_id, source_system),
            )
            conn.commit()
        return

    with _sqlite_connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO overrides (
                event_id, med_order_id, override_reason, actor_role, doctor_id, sync_status, source_system
            )
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
            """,
            (event_id, med_order_id, override_reason, actor_role, doctor_id, source_system),
        )
        conn.commit()


def get_metrics() -> dict[str, Any]:
    init_db()
    if _backend() == "postgres":
        with _postgres_connect() as conn:
            intakes = conn.execute("SELECT urgency_level, red_flags_json FROM intake_events").fetchall()
            unsafe_count = conn.execute("SELECT COUNT(*) AS c FROM dose_checks WHERE safe = FALSE").fetchone()["c"]
            override_count = conn.execute("SELECT COUNT(*) AS c FROM overrides").fetchone()["c"]
    else:
        with _sqlite_connect() as conn:
            intakes = conn.execute("SELECT urgency_level, red_flags_json FROM intake_events").fetchall()
            unsafe_count = conn.execute("SELECT COUNT(*) AS c FROM dose_checks WHERE safe = 0").fetchone()["c"]
            override_count = conn.execute("SELECT COUNT(*) AS c FROM overrides").fetchone()["c"]

    urgency_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "EMERGENCY": 0}
    red_flag_counter: Counter[str] = Counter()
    for row in intakes:
        level = (row["urgency_level"] or "").upper()
        if level in urgency_distribution:
            urgency_distribution[level] += 1
        raw_flags = row["red_flags_json"] or []
        flags = raw_flags if isinstance(raw_flags, list) else json.loads(raw_flags)
        red_flag_counter.update(flags)

    top_red_flags = [{"flag": flag, "count": count} for flag, count in red_flag_counter.most_common(5)]

    return {
        "total_intakes": len(intakes),
        "urgency_distribution": urgency_distribution,
        "top_red_flags": top_red_flags,
        "unsafe_dose_warnings": unsafe_count,
        "overrides": override_count,
    }


def list_unsynced_events(limit_per_table: int = 200) -> EventMap:
    init_db()
    events: EventMap = {table: [] for table in TABLES}
    if _backend() == "postgres":
        with _postgres_connect() as conn:
            for table in TABLES:
                rows = conn.execute(
                    f"SELECT * FROM {table} WHERE sync_status = 'pending' ORDER BY created_at ASC LIMIT %s",
                    (limit_per_table,),
                ).fetchall()
                events[table] = [dict(row) for row in rows]
        return events

    with _sqlite_connect() as conn:
        for table in TABLES:
            rows = conn.execute(
                f"SELECT * FROM {table} WHERE sync_status = 'pending' ORDER BY created_at ASC LIMIT ?",
                (limit_per_table,),
            ).fetchall()
            events[table] = [dict(row) for row in rows]
    return events


def mark_events_synced(table: str, event_ids: list[str]) -> None:
    if table not in TABLES or not event_ids:
        return
    init_db()
    if _backend() == "postgres":
        with _postgres_connect() as conn:
            conn.execute(
                f"""
                UPDATE {table}
                SET sync_status = 'synced', last_synced_at = NOW()
                WHERE event_id = ANY(%s)
                """,
                (event_ids,),
            )
            conn.commit()
        return

    placeholders = ",".join("?" for _ in event_ids)
    with _sqlite_connect() as conn:
        conn.execute(
            f"""
            UPDATE {table}
            SET sync_status = 'synced', last_synced_at = CURRENT_TIMESTAMP
            WHERE event_id IN ({placeholders})
            """,
            tuple(event_ids),
        )
        conn.commit()
