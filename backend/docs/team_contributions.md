# CLINIQ-FLOW – Team Contribution Log

## Project Scope (Friday Vertical Slice)

Nurse intake → Triage → Summary → Dose-check → Override → Admin metrics

---

## AI ENGINEERS

### Deborah

- API contract definition
- System architecture
- Orchestration pipeline
- Guardrails enforcement
- Demo narrative design

Files:

- docs/api_contract_v1.md
- services/orchestration/pipeline.py
- services/rag/guardrails.py
- schemas/*

---

### Kenny (Clinical Structuring)

- Deterministic triage rules
- SOAP formatter
- Schema validators
- Clinical rule documentation

Files:

- services/nlp/triage_rules.py
- services/nlp/soap_formatter.py
- services/nlp/validators.py
- docs/clinical_rules/*

---

### Abdulmalik (ASR)

- Whisper integration
- Accent post-processing
- Transcription reliability

Files:

- services/asr/whisper_runner.py
- services/asr/post_process.py

---

### Hamid (ASR Evaluation)

- WER/CER evaluation
- Noise testing
- Improvement metrics logging

Files:

- services/asr/eval.py

---

## AI DEVELOPERS

### Olamide (Backend Integration)

- FastAPI endpoint wiring
- Intake orchestration endpoint
- Dose-check endpoint

Files:

- api/nlp_routes.py
- api/orchestration_routes.py

---

### Adeboye (Offline + Storage)

- SQLite storage layer
- Local persistence logic
- Config management

Files:

- utils/storage.py
- utils/config.py

---

### Ayomide (Logging + Monitoring)

- Audit trail
- Request tracing
- Admin metrics endpoint

Files:

- utils/logging.py
- middleware/*
- /admin/metrics endpoint

---

### Esther (Frontend – Nurse Intake)

- Intake UI
- API integration
- Urgency badge display

Files:

- screens/NurseIntake.tsx
- services/api.ts

---

### Bolu (Frontend – Doctor View)

- SOAP display
- Dose-check UI
- Override modal

Files:

- screens/DoctorView.tsx
