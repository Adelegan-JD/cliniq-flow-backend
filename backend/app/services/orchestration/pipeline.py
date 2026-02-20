# Purpose: Validate → triage → SOAP → guardrails → return response.


import uuid
from app.services.nlp.triage_rules import evaluate_triage
from app.services.nlp.soap_formatter import build_soap
from app.services.rag.guardrails import apply_guardrails


def process_intake(intake: dict) -> dict:
    triage = evaluate_triage(intake.get("symptoms_text", ""))
    soap = build_soap(intake, triage)

    # For Friday, we guardrail the combined summary text (optional)
    combined = f"S: {soap['S']}\nO: {soap['O']}\nA: {soap['A']}\nP: {soap['P']}"
    safe = apply_guardrails(combined)

    return {
        "visit_id": intake.get("visit_id"),
        "triage": triage,
        "summary": {"soap": soap, "disclaimer": safe["disclaimer"]},
        "audit_event_id": str(uuid.uuid4()),
    }
