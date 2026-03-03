# CLINIQ-FLOW Demo Runbook

## Start backend

```powershell
cd backend
uvicorn app.main:app --reload
```

## Database mode

Default is SQLite. To use local Postgres:

```powershell
$env:CLINIQ_DB_BACKEND="postgres"
$env:DATABASE_URL_LOCAL="postgresql://postgres:password@localhost:5432/cliniq_flow_local"
```

Optional Supabase sync target:

```powershell
$env:DATABASE_URL_SUPABASE="postgresql://<user>:<password>@<host>:5432/postgres?sslmode=require"
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
- `GET /admin/sync/status` as `X-Role: admin`
- `POST /admin/sync/run` as `X-Role: admin`

## UI routing groups

Record Officer frontend can use:
- `POST /record-officer/patients`
- `GET /record-officer/patients/{patient_id}`
- `POST /record-officer/visits`
- `GET /record-officer/visits/{visit_id}`

Nurse frontend can use:
- `POST /nurse/process-intake`
- `POST /nurse/triage`
- `POST /nurse/summary`
- `GET /nurse/visits/{visit_id}/latest-intake`

## Required headers by role

- Nurse/doctor/admin routes require `X-Role`.
- Override accepts optional `X-Doctor-Id` for audit metadata.

## Synthetic payload examples

- Intake text example:
  - `"fever, cough, fast breathing since yesterday"`
- Unsafe dose example:
  - Amoxicillin `1600 mg/day` for `18 kg` child to trigger warnings.
