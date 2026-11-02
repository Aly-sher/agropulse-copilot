"""Unit tests for the RAG Orchestrator and Chemical Guardrails."""

import pytest
from app.schemas import Diagnosis, ConditionProbability, SafetyTier, SeverityBand, ActionWindow
from app.rag_engine.orchestrator import generate_farmer_advice

def test_rag_chemical_guardrail_blocks_unsafe_chemical() -> None:
    """Test that the Pydantic validator blocks hallucinated, unsafe chemical names."""
    # We will mock the LLM response by temporarily patching, but for this test, 
    # we can directly test the Pydantic model validation which the orchestrator uses.
    from app.schemas import Advice
    
    with pytest.raises(ValueError) as exc_info:
        Advice(
            summary="Test",
            confidence_statement="Test",
            do_today=[],
            monitor=[],
            escalate_if=[],
            chemical_options=["DangerousUnapprovedChemicalXYZ 99%"], # Should be blocked
            action_window=ActionWindow(can_spray_today=True, irrigation_due_hours=0, wind_warning=False)
        )
    
    assert "Unsafe or unverified chemical" in str(exc_info.value)

def test_rag_chemical_guardrail_allows_safe_chemical() -> None:
    """Test that approved chemicals pass the guardrail."""
    from app.schemas import Advice
    
    advice = Advice(
        summary="Test",
        confidence_statement="Test",
        do_today=[],
        monitor=[],
        escalate_if=[],
        chemical_options=["Propiconazole 0.1%"], # Should pass
        action_window=ActionWindow(can_spray_today=True, irrigation_due_hours=0, wind_warning=False)
    )
    
    assert len(advice.chemical_options) == 1
    assert "Propiconazole" in advice.chemical_options[0]