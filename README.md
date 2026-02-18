# 🏥 Cliniq-Flow

## AI-Assisted Clinical Workflow System

Multilingual ASR • Structured Intake • Urgency Detection • Safe Medication Validation

> Capstone Project — AI Systems Design for Clinical Workflows
>
> Designed to demonstrate responsible AI integration in healthcare environments.

---

## 🎯 Project Objective

Cliniq-Flow is an assistive clinical workflow system that integrates multilingual speech recognition, structured symptom extraction, urgency detection, and medication validation into a clinician-in-the-loop architecture.

This project explores how AI can be safely embedded into healthcare workflows without bypassing human oversight.

---

## 🚨 Problem Context

In many healthcare environments:

* Documentation is manual and time-intensive
* Voice transcription struggles with regional accents
* Intake data is unstructured
* AI outputs are not auditable
* Medication validation lacks system-level logging

Uncontrolled AI usage in healthcare introduces safety and regulatory risks.

Cliniq-Flow was designed to address these issues through structured, auditable, and guardrailed AI services.

---

## 🧠 System Capabilities

### 1️⃣ Multilingual ASR Layer

* Whisper-based speech recognition
* Supports English, Yoruba, Nigerian Pidgin
* Accent normalization pipeline
* Confidence-aware transcription

### 2️⃣ Structured Clinical Extraction

* Converts free-text into JSON clinical schema
* Symptom tagging
* Duration parsing
* Severity classification
* Red-flag identification

### 3️⃣ Urgency & Triage Engine

* Rule-based red flag detection
* Escalation flags (non-diagnostic)
* Risk category output

### 4️⃣ Dose-Check Engine

* Medication validation logic
* Deterministic rule engine
* Override logging
* Audit-safe design

### 5️⃣ Governance & Observability

* Clinician override requirement
* Admin dashboard monitoring
* Usage metrics
* Audit logging

## 🏗 Architecture Design

Cliniq-Flow is built using a modular AI services architecture:

<pre class="overflow-visible! px-0!" data-start="2590" data-end="2836"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(var(--sticky-padding-top)+9*var(--spacing))]"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>Frontend (React + Tailwind)
        ↓
FastAPI Backend
        ↓
ASR Service (Whisper)
        ↓
Normalization Layer
        ↓
Structured Clinical Engine
        ↓
Triage Engine
        ↓
Dose-Check Engine
        ↓
Audit Logging & Metrics
</span></span></code></div></div></pre>

### Architectural Principles

* Clinician-in-the-loop
* Deterministic logic for safety-critical tasks
* Audit-first design
* Service modularization for future model upgrades
* Backend separation of AI services
* Extensible for offline-first hospital environments

---

## 🛠 Tech Stack

### Backend

* FastAPI
* SQLAlchemy
* Supabase (PostgreSQL)
* Python

### AI Layer

* Whisper (ASR)
* Rule-based normalization
* Structured extraction engine
* Red-flag triage logic
* Dose-check validation engine

### Frontend

* React
* TailwindCSS

---

## 📂 Project Structure

<pre class="overflow-visible! px-0!" data-start="3403" data-end="3532"><div class="contain-inline-size rounded-2xl corner-superellipse/1.1 relative bg-token-sidebar-surface-primary"><div class="sticky top-[calc(var(--sticky-padding-top)+9*var(--spacing))]"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre!"><span><span>backend/
  app/
    api/
    models/
    services/
      asr/
      nlp/
      triage/
      dose_check/

frontend/
docs/
</span></span></code></div></div></pre>

AI capabilities are separated into domain-specific services to allow independent scaling and future model replacement.

---

## 🔌 Core API Endpoints

| Endpoint                  | Purpose                              |
| ------------------------- | ------------------------------------ |
| POST /upload              | Upload patient audio                 |
| POST /asr/transcribe      | Generate transcription               |
| POST /ai/triage           | Run urgency detection                |
| POST /ai/summary          | Generate structured clinical summary |
| POST /ai/dose-check       | Validate medication dosage           |
| POST /med-orders/override | Log clinician override               |
| GET /admin/metrics        | Retrieve system metrics              |

---

## 📊 Evaluation Focus

As a capstone project, the system tracks:

* Word Error Rate (ASR accuracy)
* Structured extraction accuracy
* Average latency (ms)
* Override frequency
* Endpoint health metrics

These metrics are intended to simulate production observability practices.

---

## 🛡 Responsible AI Considerations

Cliniq-Flow:

* Does not diagnose
* Does not prescribe
* Does not auto-approve medication
* Requires human confirmation
* Logs overrides
* Provides traceability

The goal is not to replace clinicians, but to assist structured workflow efficiency while maintaining accountability.

---

## 🔒 Data & Deployment Considerations

* Designed for private infrastructure deployment
* No hard-coded PHI
* Database abstraction via ORM
* Extendable for containerization (future work)

---

## 📌 Capstone Scope

This project demonstrates:

* AI system architecture in healthcare
* Multilingual ASR integration
* Structured NLP pipeline design
* Rule-based safety logic implementation
* Observability-first engineering

It is not intended for live clinical deployment without regulatory review and formal validation.

---

## 🚀 Future Enhancements

* Model fine-tuning for local accent datasets
* RAG-based guideline ingestion
* Offline synchronization module
* Containerized deployment (Docker)
* Performance benchmarking suite
* Integration with EMR systems
