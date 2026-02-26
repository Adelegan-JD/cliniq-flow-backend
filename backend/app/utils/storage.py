from __future__ import annotations

import json
import os
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


def _db_path() -> str:
    env_path = os.getenv("CLINIQ_DB_PATH")
    if env_path:
        return env_path
    base = Path(__file__).resolve().parents[2]
    data_dir = base / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir / "cliniq_flow.db")


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intake_events (
                event_id TEXT PRIMARY KEY,
                visit_id TEXT NOT NULL,
                urgency_level TEXT NOT NULL,
                red_flags_json TEXT NOT NULL,
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
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def log_intake(event_id: str, visit_id: str, urgency_level: str, red_flags: list[str]) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO intake_events (event_id, visit_id, urgency_level, red_flags_json)
            VALUES (?, ?, ?, ?)
            """,
            (event_id, visit_id, urgency_level, json.dumps(red_flags)),
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
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO dose_checks (
                event_id, visit_id, drug_name, chosen_dose_mg_per_day, safe, warnings_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (event_id, visit_id, drug_name, chosen_dose_mg_per_day, int(safe), json.dumps(warnings)),
        )
        conn.commit()


def log_override(event_id: str, med_order_id: str, override_reason: str, actor_role: str, doctor_id: str | None) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO overrides (event_id, med_order_id, override_reason, actor_role, doctor_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (event_id, med_order_id, override_reason, actor_role, doctor_id),
        )
        conn.commit()


def get_metrics() -> dict[str, Any]:
    init_db()
    with _connect() as conn:
        intakes = conn.execute("SELECT urgency_level, red_flags_json FROM intake_events").fetchall()
        unsafe_count = conn.execute("SELECT COUNT(*) AS c FROM dose_checks WHERE safe = 0").fetchone()["c"]
        override_count = conn.execute("SELECT COUNT(*) AS c FROM overrides").fetchone()["c"]

    urgency_distribution = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "EMERGENCY": 0}
    red_flag_counter: Counter[str] = Counter()
    for row in intakes:
        level = (row["urgency_level"] or "").upper()
        if level in urgency_distribution:
            urgency_distribution[level] += 1
        flags = json.loads(row["red_flags_json"] or "[]")
        red_flag_counter.update(flags)

    top_red_flags = [{"flag": flag, "count": count} for flag, count in red_flag_counter.most_common(5)]

    return {
        "total_intakes": len(intakes),
        "urgency_distribution": urgency_distribution,
        "top_red_flags": top_red_flags,
        "unsafe_dose_warnings": unsafe_count,
        "overrides": override_count,
    }
