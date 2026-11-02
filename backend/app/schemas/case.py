from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .advice import Advice
from .diagnosis import Diagnosis


class Case(BaseModel):
    """The master record for a single farmer interaction. Every case is a reproducible record."""

    case_id: UUID = Field(default_factory=uuid4, description="Unique identifier for the case.")
    farmer_id_hash: str = Field(..., description="Hashed identifier for the farmer to preserve privacy.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of case creation.")
    image_hash: str = Field(..., description="Perceptual hash of the uploaded image for deduplication.")

    # The core outputs
    diagnosis: Diagnosis | None = Field(None, description="The structured diagnosis output.")
    advice: Advice | None = Field(None, description="The structured advice output.")

    # State tracking
    is_resolved: bool = Field(False, description="Whether the case has been fully resolved or escalated.")
