# CLINIQ-FLOW Demo Runbook

## Start backend

```powershell
cd backend
uvicorn app.main:app --reload
```

## Run automated smoke flow

In a new terminal:

```powershell
cd backend
python scripts/smoke_test.py
```

This executes:
- `POST /ai/process_intake` as `X-Role: nurse`
- `POST /ai/dose-check` as `X-Role: doctor`
- `POST /med-orders/{id}/override` as `X-Role: doctor`
- `GET /admin/metrics` as `X-Role: admin`

## Required headers by role

- Nurse/doctor/admin routes require `X-Role`.
- Override accepts optional `X-Doctor-Id` for audit metadata.

## Synthetic payload examples

- Intake text example:
  - `"fever, cough, fast breathing since yesterday"`
- Unsafe dose example:
  - Amoxicillin `1600 mg/day` for `18 kg` child to trigger warnings.
