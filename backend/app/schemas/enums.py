from enum import Enum


class SafetyTier(str, Enum):
    """Deterministic safety tiers assigned by the policy layer."""

    GREEN = "GREEN"  # High confidence, well-covered, low-risk
    AMBER = "AMBER"  # Medium confidence, ask clarifying question, low-risk actions only
    RED = "RED"  # Low confidence, OOD, high-risk, or quarantine pest. Human escalation.
    RETAKE = "RETAKE"  # Image quality gate failed.


class SeverityBand(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
