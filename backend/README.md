# CLINIQ-FLOW

**Offline-First Clinical Decision Support System**

AI-assisted intake, rule-based triage, structured clinical summaries, and pediatric dose-checking — built for public hospital environments with limited connectivity.

---

## 📌 Project Overview

CLINIQ-FLOW is a clinical decision-support system designed to reduce risk during three critical workflow moments in public hospitals:

1. **Patient Intake**
2. **Triage & Urgency Classification**
3. **Pediatric Dose Validation**

The system does  **not diagnose or prescribe** . It supports clinicians by:

* Flagging red flags
* Assigning urgency levels (rule-based)
* Generating structured SOAP summaries
* Validating pediatric medication doses
* Logging overrides for accountability
* Providing aggregated admin metrics

It is designed to work **offline-first** and is integration-ready for future EMR systems.

---

## 🎯 Week 1 Goal (Foundation Phase)

Week 1 focuses on building the vertical demo slice:

**Intake → Triage → SOAP → Dose-Check → Admin Metrics**

This includes:

* API contract freeze
* Core orchestration pipeline
* Deterministic triage rules
* Guardrails enforcement
* Endpoint wiring
* Local database setup
* Audit logging

---

## 🏗️ System Architecture

### Frontend

* React (Web interface)
* Nurse view
* Doctor view
* Admin dashboard

### Backend

* FastAPI (Python)
* Rule-first safety engine
* SQLite (offline-first persistence)

### Core Flow

<pre class="overflow-visible! px-0!" data-start="1650" data-end="1791"><div class="w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border corner-superellipse/1.1 border-token-border-light bg-token-bg-elevated-secondary rounded-3xl"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="pointer-events-none absolute inset-x-px top-6 bottom-6"><div class="sticky z-1!"><div class="bg-token-bg-elevated-secondary sticky"></div></div></div><div class="corner-superellipse/1.1 rounded-3xl bg-token-bg-elevated-secondary"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>Intake Request</span><br/><span>     ↓</span><br/><span>Validation</span><br/><span>     ↓</span><br/><span>Triage Rules Engine</span><br/><span>     ↓</span><br/><span>SOAP Formatter</span><br/><span>     ↓</span><br/><span>Guardrails Layer</span><br/><span>     ↓</span><br/><span>Response to Frontend</span></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## 📂 Backend Folder Structure

<pre class="overflow-visible! px-0!" data-start="1830" data-end="2382"><div class="w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border corner-superellipse/1.1 border-token-border-light bg-token-bg-elevated-secondary rounded-3xl"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="pointer-events-none absolute inset-x-px top-6 bottom-6"><div class="sticky z-1!"><div class="bg-token-bg-elevated-secondary sticky"></div></div></div><div class="corner-superellipse/1.1 rounded-3xl bg-token-bg-elevated-secondary"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>backend/</span><br/><span>│</span><br/><span>├── app/</span><br/><span>│   ├── api/                  # Route definitions (thin controllers)</span><br/><span>│   ├── services/</span><br/><span>│   │   ├── orchestration/    # Intake pipeline</span><br/><span>│   │   ├── nlp/              # Triage rules, SOAP, validators</span><br/><span>│   │   ├── rag/              # Guardrails logic</span><br/><span>│   │   ├── asr/              # Whisper transcription (optional)</span><br/><span>│   ├── schemas/              # Pydantic request/response models</span><br/><span>│   ├── utils/                # Logging, config, storage</span><br/><span>│   └── main.py               # FastAPI entry point</span><br/><span>│</span><br/><span>└── docs/</span><br/><span>    └── api_contract_v1.md</span></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## 🚀 Running the Backend

From the `backend` directory:

<pre class="overflow-visible! px-0!" data-start="2447" data-end="2488"><div class="w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border corner-superellipse/1.1 border-token-border-light bg-token-bg-elevated-secondary rounded-3xl"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="pointer-events-none absolute inset-x-px top-6 bottom-6"><div class="sticky z-1!"><div class="bg-token-bg-elevated-secondary sticky"></div></div></div><div class="corner-superellipse/1.1 rounded-3xl bg-token-bg-elevated-secondary"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>uvicorn app.main:app </span><span class="ͼu">--reload</span></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Server runs at:

<pre class="overflow-visible! px-0!" data-start="2506" data-end="2535"><div class="w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border corner-superellipse/1.1 border-token-border-light bg-token-bg-elevated-secondary rounded-3xl"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="pointer-events-none absolute inset-x-px top-6 bottom-6"><div class="sticky z-1!"><div class="bg-token-bg-elevated-secondary sticky"></div></div></div><div class="corner-superellipse/1.1 rounded-3xl bg-token-bg-elevated-secondary"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>http://127.0.0.1:8000</span></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

Swagger Docs:

<pre class="overflow-visible! px-0!" data-start="2551" data-end="2585"><div class="w-full my-4"><div class=""><div class="relative"><div class="h-full min-h-0 min-w-0"><div class="h-full min-h-0 min-w-0"><div class="border corner-superellipse/1.1 border-token-border-light bg-token-bg-elevated-secondary rounded-3xl"><div class="pointer-events-none absolute inset-x-4 top-12 bottom-4"><div class="pointer-events-none sticky z-40 shrink-0 z-1!"><div class="sticky bg-token-border-light"></div></div></div><div class="pointer-events-none absolute inset-x-px top-6 bottom-6"><div class="sticky z-1!"><div class="bg-token-bg-elevated-secondary sticky"></div></div></div><div class="corner-superellipse/1.1 rounded-3xl bg-token-bg-elevated-secondary"><div class="relative z-0 flex max-w-full"><div id="code-block-viewer" dir="ltr" class="q9tKkq_viewer cm-editor z-10 light:cm-light dark:cm-light flex h-full w-full flex-col items-stretch ͼk ͼy"><div class="cm-scroller"><div class="cm-content q9tKkq_readonly"><span>http://127.0.0.1:8000/docs</span></div></div></div></div></div></div></div></div><div class=""><div class=""></div></div></div></div></div></pre>

---

## 🔌 MVP Endpoints (Week 1)

### Core Clinical Flow

| Method | Endpoint                      | Purpose                                |
| ------ | ----------------------------- | -------------------------------------- |
| POST   | `/ai/process_intake`        | Intake → triage → SOAP → disclaimer |
| POST   | `/ai/dose-check`            | Validate pediatric medication dose     |
| POST   | `/visits/{id}/med-order`    | Create medication order                |
| POST   | `/med-orders/{id}/override` | Submit override with reason            |

### Monitoring

| Method | Endpoint           | Purpose                            |
| ------ | ------------------ | ---------------------------------- |
| GET    | `/admin/metrics` | Aggregated counts (no identifiers) |
| GET    | `/health`        | System health check                |

### Optional Enhancement

| Method | Endpoint            | Purpose              |
| ------ | ------------------- | -------------------- |
| POST   | `/asr/transcribe` | Voice-to-text intake |

---

## 🛡️ Safety Principles

* Rule-based triage (no probabilistic urgency classification)
* Deterministic dose-check ranges
* No autonomous diagnosis
* No prescription generation
* Mandatory override justification
* Admin metrics exclude patient identifiers

---

## 👥 Team Responsibilities (Week 1)

### Deborah

* API contract freeze
* Orchestration pipeline
* Guardrails enforcement

### Kenny

* Triage rules engine
* SOAP formatter
* Data validators

### Olamide

* Endpoint wiring
* Doctor action endpoints

### Adeboye

* Postgres persistence
* Visit linking

### Ayomide

* Audit logging
* Admin metrics endpoint

### Abdulmalik

* ASR transcription endpoint

### Hamid

* ASR evaluation (WER/CER metrics)

---

## 📊 Admin Metrics Include

* Total intakes
* Urgency distribution
* Red flag frequency
* Dose-check warnings
* Override count

(No patient names exposed.)

---

## ⚠️ Current Scope (Friday Demo)

**In Scope:**

* Typed intake
* Deterministic triage
* Structured summary
* Dose warning
* Override logging
* Metrics dashboard

**Out of Scope (Future):**

* Full EMR integration
* Full drug formulary
* Advanced AI diagnostic reasoning
* Cloud deployment

---

## 📅 Project Timeline

**Week 1 — Foundation**

Architecture + core logic + endpoint structure

**Week 2 — Integration**

Frontend wiring + persistence + flow stabilization

**Week 3 — Demo & Hardening**

Testing + documentation + stakeholder walkthrough

---

## 🧠 Design Philosophy

CLINIQ-FLOW is:

* Safety-first
* Explainable
* Minimalistic
* Offline-capable
* Clinician-supportive (not clinician-replacing)
