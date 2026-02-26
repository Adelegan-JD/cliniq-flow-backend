# CLINIQ-FLOW API Contract v1 (Friday Demo)

Base URL: <http://localhost:8000>
Urgency enum: LOW | MEDIUM | HIGH | EMERGENCY

## POST /ai/process_intake

Input:

```json
{
  "visit_id": "uuid",
  "age_years": 5,
  "weight_kg": 18,
  "symptoms_text": "fever, cough, fast breathing since yesterday",
  "duration_days": 1,
  "vitals": {"rr": 40, "temp_c": 39.2}
}
```

Output:
{
  "visit_id": "uuid",
  "triage": {
    "urgency_level": "HIGH",
    "red_flags": ["difficulty_breathing"],
    "reasons": ["Fast breathing suggests possible respiratory distress"]
  },
  "summary": {
    "soap": {"S": "...", "O": "...", "A": "...", "P": "..."},
    "disclaimer": "CLINIQ-FLOW provides decision support and does not diagnose or prescribe."
  },
  "audit_event_id": "uuid"
}

## POST /ai/dose_check

Input:
{
  "visit_id": "uuid",
  "drug": "amoxicillin",
  "age_years": 5,
  "weight_kg": 18,
  "frequency_per_day": 2,
  "chosen_dose_mg_per_day": 700
}

Output:
{
  "safe": false,
  "warnings": ["Dose exceeds recommended mg/kg/day range"],
  "recommended_range_mg_per_day": {"min": 360, "max": 540},
  "max_mg_per_day": 540,
  "event_id": "uuid",
  "allow_override": true
}

## GET /admin/metrics

Output:
{
  "total_intakes": 12,
  "urgency_distribution": {"LOW": 3, "MEDIUM": 5, "HIGH": 3, "EMERGENCY": 1},
  "top_red_flags": [{"flag": "difficulty_breathing", "count": 4}],
  "unsafe_dose_warnings": 2,
  "overrides": 1
}
Error format
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "weight_kg is required",
    "details": {"field": "weight_kg"}
  }
}

## POST /med-orders/{id}/override

Input:

{
  "reason": "Clinical judgment based on patient history"
}

Output:

{
  "override_logged": true,
  "event_id": "uuid"
}

## GET /health

Output:

{
  "status": "ok"
}

### Field Validation Rules

- visit_id: required, UUID
- age_years: required, integer >= 0
- weight_kg: required, float > 0
- symptoms_text: required, non-empty string
- duration_days: optional, integer >= 0
- vitals: optional object

- drug: required, string
- frequency_per_day: required, integer >= 1
- chosen_dose_mg_per_day: required, integer > 0

### HTTP Status Codes

200 — Success  
400 — Validation Error  
404 — Resource Not Found  
500 — Internal Server Error  

### Privacy & Safety

All intake text is de-identified before processing and storage.
The system provides decision support only and does not diagnose or prescribe.