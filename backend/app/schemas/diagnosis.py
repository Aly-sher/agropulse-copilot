from typing import Optional

from pydantic import BaseModel, Field

from .enums import SafetyTier, SeverityBand


class ConditionProbability(BaseModel):
    condition_id: str = Field(
        ..., description="Unique identifier for the diagnosed condition (e.g., 'wheat_yellow_rust')."
    )
    probability: float = Field(..., ge=0.0, le=1.0, description="Calibrated probability of the condition.")
    is_in_conformal_set: bool = Field(
        ..., description="Whether this condition is in the statistical conformal prediction set."
    )


class Diagnosis(BaseModel):
    """The structured, calibrated output from the Vision and OOD pipeline."""

    prediction_set: list[ConditionProbability] = Field(
        ..., description="Calibrated, conformal prediction set."
    )
    tier: SafetyTier = Field(..., description="Deterministic safety tier assigned by the policy layer.")
    severity: Optional[SeverityBand] = Field(None, description="Estimated severity band of the condition.")
    symptoms_seen: list[str] = Field(default_factory=list, description="Symptoms identified by the VLM.")
    ood_score: float = Field(..., ge=0.0, description="Out-of-distribution score for the input image.")
    model_versions: dict[str, str] = Field(
        ..., description="Dictionary of model names to their version hashes for auditability."
    )
