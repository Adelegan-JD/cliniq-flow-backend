# CLINIQ-FLOW API Contract v1 (Friday Demo)

Base URL: http://localhost:8000
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

## POST /ai/pdose_check

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
  "recommended_range_mg_per_day": [360, 540],
  "max_mg_per_day": 540,
  "event_id": "uuid",
  "allow_override": true
}

## GET/admin/metrics

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

