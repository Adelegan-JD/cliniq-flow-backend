from __future__ import annotations

import os
from pathlib import Path

from fastapi.testclient import TestClient


def _client(tmp_path: Path) -> TestClient:
    os.environ["CLINIQ_DB_PATH"] = str(tmp_path / "test_cliniq.db")
    from app.main import app

    return TestClient(app)


def test_health_and_root(tmp_path: Path) -> None:
    client = _client(tmp_path)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    root = client.get("/")
    assert root.status_code == 200
    assert "docs" in root.json()


def test_process_intake_contract_shape(tmp_path: Path) -> None:
    client = _client(tmp_path)
    payload = {
        "visit_id": "visit-001",
        "age_years": 5,
        "weight_kg": 18,
        "symptoms_text": "my name is John Doe, fever and fast breathing since yesterday",
        "duration_days": 1,
        "vitals": {"rr": 40, "temp_c": 39.2},
    }
    response = client.post("/ai/process_intake", json=payload, headers={"X-Role": "nurse"})
    assert response.status_code == 200
    body = response.json()
    assert set(["visit_id", "triage", "summary", "audit_event_id"]).issubset(body.keys())
    assert "urgency_level" in body["triage"]


def test_dose_check_unsafe_and_safe(tmp_path: Path) -> None:
    client = _client(tmp_path)
    common = {
        "visit_id": "visit-dose",
        "drug": "amoxicillin",
        "age_years": 5,
        "weight_kg": 18,
        "frequency_per_day": 2,
    }
    unsafe = client.post(
        "/ai/dose-check",
        json={**common, "chosen_dose_mg_per_day": 2000},
        headers={"X-Role": "doctor"},
    )
    assert unsafe.status_code == 200
    assert unsafe.json()["safe"] is False
    assert unsafe.json()["allow_override"] is True

    safe = client.post(
        "/ai/dose-check",
        json={**common, "chosen_dose_mg_per_day": 500},
        headers={"X-Role": "doctor"},
    )
    assert safe.status_code == 200
    assert safe.json()["safe"] is True


def test_override_and_metrics(tmp_path: Path) -> None:
    client = _client(tmp_path)
    client.post(
        "/ai/process_intake",
        json={
            "visit_id": "visit-metrics",
            "age_years": 4,
            "weight_kg": 16,
            "symptoms_text": "convulsion and fever",
            "duration_days": 1,
            "vitals": {"rr": 38},
        },
        headers={"X-Role": "nurse"},
    )
    client.post(
        "/ai/dose-check",
        json={
            "visit_id": "visit-metrics",
            "drug": "amoxicillin",
            "age_years": 4,
            "weight_kg": 16,
            "frequency_per_day": 2,
            "chosen_dose_mg_per_day": 9999,
        },
        headers={"X-Role": "doctor"},
    )
    override = client.post(
        "/med-orders/m1/override",
        json={"reason": "Clinically justified by prior specialist recommendation"},
        headers={"X-Role": "doctor", "X-Doctor-Id": "doc-123"},
    )
    assert override.status_code == 200
    assert override.json()["override_logged"] is True

    metrics = client.get("/admin/metrics", headers={"X-Role": "admin"})
    assert metrics.status_code == 200
    body = metrics.json()
    assert body["total_intakes"] >= 1
    assert body["unsafe_dose_warnings"] >= 1
    assert body["overrides"] >= 1


def test_error_shape_for_validation_and_forbidden(tmp_path: Path) -> None:
    client = _client(tmp_path)
    forbidden = client.get("/admin/metrics", headers={"X-Role": "nurse"})
    assert forbidden.status_code == 403
    assert "error" in forbidden.json()

    invalid = client.post("/ai/process_intake", json={"visit_id": "x"}, headers={"X-Role": "nurse"})
    assert invalid.status_code == 422
    assert invalid.json()["error"]["code"] == "VALIDATION_ERROR"
