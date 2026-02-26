import enum


class VisitStatus(str, enum.Enum):
    REGISTERED = "registered"
    INTAKE_COMPLETED = "intake_completed"
    AI_PROCESSED = "ai_processed"
    DOCTOR_REVIEWED = "doctor_reviewed"
    CLOSED = "closed"


class UrgencyLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
