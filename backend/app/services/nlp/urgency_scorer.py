"""
Computes urgency level from vital signs only.

Flow:
Nurse enters vitals (temp, HR, RR, weight, height, SpO2) →
urgency_scorer computes level →
Nurse sees urgency badge (Red/Yellow/Green) →
Doctor reviews full assessment


Universal triage scoring module (0-100+ years).

Vitals Supported:
- Temperature
- Heart Rate
- Respiratory Rate
- Blood Pressure (systolic/diastolic)
- Weight
- Height (optional for BMI)

Outputs:
- EMERGENCY (Red)
- URGANT (Yellow)
- NORMAL (Green)
"""

from __future__ import annotations


from enum import Enum
from typing import List, Optional

from models.clinical_schema import PatientDemographics, VitalSign



# URGENCY LEVELS

class UrgencyLevel(str, Enum):
    EMERGENCY = "emergency"
    URGENT = "urgent"
    NORMAL = "normal"


class UrgencyScore:
    def __init__(
        self,
        level: UrgencyLevel,
        score: int,
        reasons: List[str],
        abnormal_vitals: List[str],
    ):
        self.level = level
        self.score = score
        self.reasons = reasons
        self.abnormal_vitals = abnormal_vitals

    def to_dict(self):
        return {
            "level": self.level.value,
            "score": self.score,
            "reasons": self.reasons,
            "abnormal_vitals": self.abnormal_vitals,
        }



# URGENCY SCORER


class UrgencyScorer:

    VITAL_RANGES = {
        "temperature": {
            "critical_low": 35.0,
            "low": 36.0,
            "normal": (36.5, 37.5),
            "high": 38.0,
            "critical_high": 40.0,
        },
        "heart_rate": {
            "adult": {"critical_low": 40, "low": 50, "normal": (60, 100), "high": 120, "critical_high": 150},
        },
        "respiratory_rate": {
            "adult": {"critical_low": 8, "low": 10, "normal": (12, 20), "high": 25, "critical_high": 35},
        },
        "blood_pressure": {
            "critical_low_sys": 70,
            "low_sys": 90,
            "normal_sys": (100, 130),
            "high_sys": 150,
            "critical_high_sys": 180,
        },
    }

    def score(self, vitals: List[VitalSign], demographics: PatientDemographics) -> UrgencyScore:

        score = 0
        reasons = []
        abnormal_vitals = []

        systolic = None
        diastolic = None

        # Check each vital
        for vital in vitals:
            name = vital.name.lower()
            try:
                value = float(vital.value)
            except (ValueError, TypeError):
                continue  # skip invalid values

            if "temp" in name:
                severity = self._assess_temperature(value)
            elif "heart" in name or "pulse" in name:
                severity = self._assess_heart_rate(value)
            elif "resp" in name or "breath" in name:
                severity = self._assess_respiratory_rate(value)
            elif "blood" in name or "pressure" in name:
                try:
                    parts = str(vital.value).split("/")
                    systolic = float(parts[0])
                    diastolic = float(parts[1])
                    continue
                except (ValueError, IndexError):
                    continue
            else:
                continue

            score, reasons, abnormal_vitals = self._update_score(
                severity, score, vital, reasons, abnormal_vitals
            )

        # Blood pressure check
        if systolic is not None:
            severity = self._assess_blood_pressure(systolic)
            if severity != "normal":
                bp_vital = VitalSign(name="Blood Pressure", value=f"{systolic}/{diastolic}", unit="mmHg")
                score, reasons, abnormal_vitals = self._update_score(
                    severity, score, bp_vital, reasons, abnormal_vitals
                )

        # BMI / Extreme Weight check

        # If height is provided, BMI is calculated and assessed.
        # If height is missing, only extreme weight triggers a warning.
        # And if weight itself is missing, skip BMI/weight checks entirely.

        if demographics.weight_kg:  # only if weight provided
            if demographics.height_cm:  # height provided → calculate BMI
               bmi = demographics.weight_kg / ((demographics.height_cm / 100) ** 2)
            if bmi < 16 or bmi > 35:  # WHO-aligned abnormal BMI
               score = max(score, 50)
               reasons.append(f"Abnormal BMI: {bmi:.1f}")
            else:  # height missing → check for extreme weight only
                if demographics.weight_kg < 30 or demographics.weight_kg > 200:
                   score = max(score, 40)
                   reasons.append("Extreme body weight detected")

        # Classification 
        if score >= 80:
            level = UrgencyLevel.EMERGENCY
        elif score >= 40:
            level = UrgencyLevel.URGENT
        else:
            level = UrgencyLevel.NORMAL

        return UrgencyScore(level, score, reasons, abnormal_vitals)


    # Assessment Helpers

    def _assess_temperature(self, value: float) -> str:
        r = self.VITAL_RANGES["temperature"]
        if value < r["critical_low"] or value > r["critical_high"]:
            return "critical"
        elif value < r["low"] or value > r["high"]:
            return "high"
        return "normal"

    def _assess_heart_rate(self, value: float) -> str:
        r = self.VITAL_RANGES["heart_rate"]["adult"]
        if value < r["critical_low"] or value > r["critical_high"]:
            return "critical"
        elif value < r["low"] or value > r["high"]:
            return "high"
        return "normal"

    def _assess_respiratory_rate(self, value: float) -> str:
        r = self.VITAL_RANGES["respiratory_rate"]["adult"]
        if value < r["critical_low"] or value > r["critical_high"]:
            return "critical"
        elif value < r["low"] or value > r["high"]:
            return "high"
        return "normal"

    def _assess_blood_pressure(self, systolic: float) -> str:
        r = self.VITAL_RANGES["blood_pressure"]
        if systolic < r["critical_low_sys"] or systolic > r["critical_high_sys"]:
            return "critical"
        elif systolic < r["low_sys"] or systolic > r["high_sys"]:
            return "high"
        return "normal"

    def _update_score(self, severity: str, score: int, vital: VitalSign, reasons: List[str], abnormal_vitals: List[str]):
        if severity == "critical":
            score = max(score, 90)
            reasons.append(f"CRITICAL: {vital.name} = {vital.value}")
            abnormal_vitals.append(vital.name)
        elif severity == "high":
            score = max(score, 50)
            reasons.append(f"Abnormal: {vital.name} = {vital.value}")
            abnormal_vitals.append(vital.name)
        return score, reasons, abnormal_vitals