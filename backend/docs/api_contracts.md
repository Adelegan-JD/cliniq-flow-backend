# CLINIQ-FLOW API Contract v1

Base URL: <http://localhost:8000>
Auth: `Authorization: Bearer <access_token>`
Urgency enum: `LOW | MEDIUM | HIGH | EMERGENCY`

## Canonical Endpoints

### POST /patients

Input:

```json
{
  "full_name": "Test Child",
  "date_of_birth": "2021-06-01",
  "gender": "female",
  "phone": "08030000000"
}
```

Output:

```json
{
  "id": "uuid-string",
  "full_name": "Test Child",
  "date_of_birth": "2021-06-01",
  "gender": "female",
  "phone": "08030000000",
  "created_at": "2026-03-04 12:00:00"
}
```

### POST /visits

Input:

```json
{
  "patient_id": "uuid-string",
  "visit_status": "open"
}
```

Output:

```json
{
  "id": "uuid-string",
  "patient_id": "uuid-string",
  "visit_status": "open",
  "created_at": "2026-03-04 12:01:00"
}
```

### POST /ai/process_intake

Input:

```json
{
  "visit_id": "uuid-string",
  "age_years": 5,
  "weight_kg": 18,
  "symptoms_text": "fever, cough, fast breathing since yesterday",
  "duration_days": 1,
  "vitals": {
    "rr": 40,
    "temp_c": 39.2
  }
}
```

Output:

```json
{
  "visit_id": "uuid-string",
  "triage": {
    "urgency_level": "HIGH",
    "red_flags": ["difficulty_breathing"],
    "reasons": ["Fast breathing suggests possible respiratory distress"]
  },
  "summary": {
    "soap": {
      "S": "...",
      "O": "...",
      "A": "...",
      "P": "..."
    },
    "disclaimer": "CLINIQ-FLOW provides decision support and does not diagnose or prescribe."
  },
  "audit_event_id": "uuid-string"
}
```

### POST /ai/triage

Input:

```json
{
  "visit_id": "uuid-string",
  "transcript": "child has fever and difficulty breathing",
  "patient_age": "5 years",
  "patient_sex": "female"
}
```

Output:

```json
{
  "visit_id": "uuid-string",
  "triage": {
    "urgency_level": "HIGH",
    "red_flags": ["difficulty_breathing"],
    "reasons": ["Fast breathing suggests possible respiratory distress"]
  }
}
```

### POST /ai/summary

Input:

```json
{
  "visit_id": "uuid-string",
  "transcript": "child has fever and cough for two days",
  "patient_age": "5 years",
  "patient_sex": "female"
}
```

Output:

```json
{
  "visit_id": "uuid-string",
  "summary": {
    "soap": {
      "S": "...",
      "O": "...",
      "A": "...",
      "P": "..."
    },
    "disclaimer": "CLINIQ-FLOW provides decision support and does not diagnose or prescribe."
  }
}
```

### POST /ai/dose-check

Input:

```json
{
  "visit_id": "uuid-string",
  "drug": "amoxicillin",
  "age_years": 5,
  "weight_kg": 18,
  "frequency_per_day": 2,
  "chosen_dose_mg_per_day": 700
}
```

Output:

```json
{
  "safe": false,
  "warnings": ["Dose exceeds recommended mg/kg/day range"],
  "recommended_range_mg_per_day": {
    "min": 360,
    "max": 720
  },
  "max_mg_per_day": 720,
  "event_id": "uuid-string",
  "allow_override": true
}
```

### POST /med-orders

Input:

```json
{
  "visit_id": "uuid-string",
  "drug_name": "amoxicillin",
  "dose_mg_per_day": 600,
  "frequency_per_day": 2,
  "is_safe": true,
  "dose_check_result": {
    "safe": true
  }
}
```

### POST /med-orders/{id}/override

Input:

```json
{
  "reason": "Clinical judgment based on patient history"
}
```

Output:

```json
{
  "override_logged": true,
  "event_id": "uuid-string",
  "med_order_id": "uuid-string"
}
```

### GET /admin/metrics

Output:

```json
{
  "total_intakes": 12,
  "urgency_distribution": {
    "LOW": 3,
    "MEDIUM": 5,
    "HIGH": 3,
    "EMERGENCY": 1
  },
  "top_red_flags": [
    {
      "flag": "difficulty_breathing",
      "count": 4
    }
  ],
  "unsafe_dose_warnings": 2,
  "overrides": 1
}
```

### GET /health

Output:

```json
{
  "status": "ok",
  "service": "cliniq-flow-backend"
}
```

## Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": []
  }
}
```

## Field Validation Rules

- `visit_id`: required string identifier
- `patient_id`: required string identifier
- `age_years`: required integer `>= 0`
- `weight_kg`: required float `> 0` for intake and dose-check
- `symptoms_text`: required non-empty string, minimum length `3`
- `duration_days`: optional integer `>= 0`
- `vitals`: optional object
- `drug`: required string
- `drug_name`: required string
- `frequency_per_day`: required integer `>= 1`
- `chosen_dose_mg_per_day`: required integer `> 0`
- `reason`: required string, minimum length `3`

## HTTP Status Codes

- `200` success
- `401` missing or invalid bearer token
- `403` authenticated but insufficient role
- `404` resource not found
- `422` request validation failed
- `500` internal server error

## Role Matrix

- Record officer: `/patients`, `/visits`, `/record-officer/*`
- Nurse: `/ai/process_intake`, `/ai/triage`, `/ai/summary`, `/nurse/*`
- Doctor: `/ai/dose-check`, `/med-orders`, `/med-orders/{id}/override`, `/visits/{id}/doctor-conversation`
- Admin: `/admin/*`

## Privacy and Safety

All intake text is de-identified before processing and storage.
The system provides decision support only and does not diagnose or prescribe.
