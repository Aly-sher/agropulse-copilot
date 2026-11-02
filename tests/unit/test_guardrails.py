"""Unit tests for the deterministic safety and policy layer."""

from app.core.guardrails import assign_safety_tier
from app.schemas import ConditionProbability, Diagnosis, SafetyTier


def test_assign_tier_green_high_confidence() -> None:
    """Test that high confidence, in-distribution cases get GREEN tier."""
    diagnosis = Diagnosis(
        prediction_set=[
            ConditionProbability(
                condition_id="wheat_yellow_rust",
                probability=0.92,
                is_in_conformal_set=True,
            )
        ],
        tier=SafetyTier.GREEN,
        severity=None,
        symptoms_seen=["yellow pustules on upper leaf surface"],
        ood_score=0.15,
        model_versions={"vision_classifier": "v1.2.0"},
    )

    assert assign_safety_tier(diagnosis) == SafetyTier.GREEN

def test_assign_tier_red_ood() -> None:
    """Test that Out-Of-Distribution images force a RED tier regardless of probability."""
    diagnosis = Diagnosis(
        prediction_set=[
            ConditionProbability(
                condition_id="wheat_yellow_rust",
                probability=0.95,
                is_in_conformal_set=True,
            )
        ],
        tier=SafetyTier.RED,
        severity=None,
        symptoms_seen=[],
        ood_score=0.85,
        model_versions={"vision_classifier": "v1.2.0"},
    )

    assert assign_safety_tier(diagnosis) == SafetyTier.RED

def test_assign_tier_red_high_risk_condition() -> None:
    """Test that known quarantine pests force a RED tier."""
    diagnosis = Diagnosis(
        prediction_set=[
            ConditionProbability(
                condition_id="quarantine_pest",
                probability=0.88,
                is_in_conformal_set=True,
            )
        ],
        tier=SafetyTier.RED,
        severity=None,
        symptoms_seen=[],
        ood_score=0.10,
        model_versions={"vision_classifier": "v1.2.0"},
    )

    assert assign_safety_tier(diagnosis) == SafetyTier.RED

def test_assign_tier_amber_ambiguous() -> None:
    """Test that medium confidence or multiple possibilities result in AMBER tier."""
    diagnosis = Diagnosis(
        prediction_set=[
            ConditionProbability(
                condition_id="wheat_yellow_rust",
                probability=0.60,
                is_in_conformal_set=True,
            ),
            ConditionProbability(
                condition_id="wheat_brown_rust",
                probability=0.35,
                is_in_conformal_set=True,
            )
        ],
        tier=SafetyTier.AMBER,
        severity=None,
        symptoms_seen=["brown spots"],
        ood_score=0.20,
        model_versions={"vision_classifier": "v1.2.0"},
    )

    assert assign_safety_tier(diagnosis) == SafetyTier.AMBER
