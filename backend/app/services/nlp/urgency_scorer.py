"""
module: Computes urgency level from clinical flags and symptoms.
This feeds directly into the nurse UI to show red/yellow/green urgency.

How it flow:
Nurse enters symptoms → extracts → urgency_scorer computes level → 
Doctor sees red flags + urgency badge

"""

from __future__ import annotations

from enum import Enum
from typing import List

from models.clinical_schema import (
    ClinicalFlag,
    Severity,
    StructuredClinicalData,
    Symptom,
)


class UrgencyLevel(str, Enum):
    """Urgency classification for triage."""
    IMMEDIATE = "immediate"      # Red - see immediately (e.g. Emergency)
    URGENT = "urgent"            # Orange
    STANDARD = "standard"        # Yellow 
    NON_URGENT = "non_urgent"    # Green - can wait, self-care advice


class UrgencyScore:
    """Urgency assessment output."""
    def __init__(
        self,
        level: UrgencyLevel,
        score: int,
        reasons: List[str],
        critical_flags: List[str],
    ):
        self.level = level
        self.score = score  # 0-100
        self.reasons = reasons
        self.critical_flags = critical_flags

    def to_dict(self):
        return {
            "level": self.level.value,
            "score": self.score,
            "reasons": self.reasons,
            "critical_flags": self.critical_flags,
        }


class UrgencyScorer:
    """
    Computes urgency level from StructuredClinicalData.
    
    Scoring logic:
    - Critical flags (convulsion, difficulty breathing) → IMMEDIATE (100)
    - Multiple high severity symptoms → URGENT (70-90)
    - Abnormal vitals + symptoms → URGENT (60-80)
    - Single moderate symptom → STANDARD (30-50)
    - Mild symptoms only → NON_URGENT (0-30)
    """

    # Danger sign symptoms that trigger immediate urgency
    CRITICAL_SYMPTOMS = {
        "convulsion",
        "difficulty_breathing",
        "altered_consciousness",
        "severe_dehydration",
        "unable_to_feed",
        "unconscious",
    }

    # High-priority symptoms
    HIGH_PRIORITY_SYMPTOMS = {
        "fever",
        "vomiting",
        "diarrhoea",
        "severe_pain",
        "bleeding",
        "chest_pain",
    }

    def score(self, data: StructuredClinicalData) -> UrgencyScore:
        """Compute urgency from clinical data."""
        score = 0
        reasons = []
        critical_flags = []

        # Check clinical flags first
        for flag in data.clinical_flags:
            if flag.severity == Severity.CRITICAL:
                score = 100
                reasons.append(f"{flag.description}")
                critical_flags.append(flag.triggered_by)
        
        if score == 100:
            return UrgencyScore(
                level=UrgencyLevel.IMMEDIATE,
                score=score,
                reasons=reasons,
                critical_flags=critical_flags,
            )

        # Check for critical symptoms
        symptom_names = {s.name for s in data.symptoms}
        critical_present = symptom_names & self.CRITICAL_SYMPTOMS
        if critical_present:
            score = max(score, 95)
            reasons.append(f"Critical symptom(s): {', '.join(critical_present)}")
            critical_flags.extend(list(critical_present))

        # High severity symptoms
        high_severity = [
            s for s in data.symptoms
            if s.severity in (Severity.HIGH, Severity.CRITICAL)
        ]
        if len(high_severity) >= 2:
            score = max(score, 80)
            reasons.append(f"Multiple severe symptoms ({len(high_severity)})")
        elif len(high_severity) == 1:
            score = max(score, 60)
            reasons.append(f"Severe symptom: {high_severity[0].name}")

        # High-priority symptom categories
        high_priority_present = symptom_names & self.HIGH_PRIORITY_SYMPTOMS
        if high_priority_present:
            score = max(score, 55)
            if not reasons:  # only add if no higher-priority reason
                reasons.append(f"Priority symptoms: {', '.join(high_priority_present)}")

        # Abnormal vitals boost score
        abnormal_vitals = [v for v in data.vital_signs if v.is_abnormal]
        if abnormal_vitals:
            vital_boost = len(abnormal_vitals) * 15
            score = max(score, 40 + vital_boost)
            reasons.append(f"Abnormal vital signs ({len(abnormal_vitals)})")

        # Age consideration (paediatric)
        if data.demographics.age:
            age_str = data.demographics.age.lower()
            if "month" in age_str or "week" in age_str:
                # Infant - increase urgency slightly
                score += 10
                reasons.append("Infant age group")

        # Default if no symptoms 
        if not data.symptoms:
            score = max(score, 20)
            reasons.append("No specific symptoms documented")

        # Determine level from score
        if score >= 90:
            level = UrgencyLevel.IMMEDIATE
        elif score >= 60:
            level = UrgencyLevel.URGENT
        elif score >= 30:
            level = UrgencyLevel.STANDARD
        else:
            level = UrgencyLevel.NON_URGENT

        return UrgencyScore(
            level=level,
            score=min(score, 100),
            reasons=reasons,
            critical_flags=critical_flags,
        )



# Example integration into NLP response building (in nlp_routes.py): 

def add_urgency_to_response(data: StructuredClinicalData) -> dict:
    """
    Call this after extraction to add urgency to the API response.
    
    Usage in nlp_routes.py:
        structured_data, method = _extractor.extract(...)
        soap_note = _formatter.format(structured_data)
        validation = _validator.validate_all(...)
        
        # Add urgency
        urgency = UrgencyScorer().score(structured_data)
        
        return {
            "session_id": session_id,
            "structured_data": structured_data.dict(),
            "soap_note": soap_note.dict(),
            "validation": validation.dict(),
            "urgency": urgency.to_dict(),
            "processing_time_ms": elapsed_ms,
        }
    """
    scorer = UrgencyScorer()
    urgency = scorer.score(data)
    return urgency.to_dict()