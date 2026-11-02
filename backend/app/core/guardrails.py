"""Deterministic safety and policy layer for AgroPulse Copilot."""

from app.schemas import Diagnosis, SafetyTier

# Enterprise-configurable thresholds (would normally come from settings)
OOD_THRESHOLD = 0.65
HIGH_CONFIDENCE_THRESHOLD = 0.85
HIGH_RISK_CONDITIONS = {"quarantine_pest", "unknown_pathogen"}

def assign_safety_tier(diagnosis: Diagnosis) -> SafetyTier:
    """
    Deterministically assign a safety tier based on model outputs.
    The LLM receives this tier as an input and CANNOT override it.
    """
    # Rule 1: If the image is Out-Of-Distribution, force RED
    if diagnosis.ood_score > OOD_THRESHOLD:
        return SafetyTier.RED

    # Rule 2: If the top prediction is a known high-risk/quarantine condition, force RED
    top_condition = diagnosis.prediction_set[0].condition_id
    if top_condition in HIGH_RISK_CONDITIONS:
        return SafetyTier.RED

    # Rule 3: If confidence is high, conformal set is small (1 item), and it's a reviewed condition -> GREEN
    if (
        len(diagnosis.prediction_set) == 1
        and diagnosis.prediction_set[0].probability >= HIGH_CONFIDENCE_THRESHOLD
        and diagnosis.prediction_set[0].is_in_conformal_set
    ):
        return SafetyTier.GREEN

    # Rule 4: Default fallback for medium confidence or ambiguous cases -> AMBER
    return SafetyTier.AMBER
