"""FastAPI endpoint for the end-to-end AI Copilot analysis."""

from fastapi import APIRouter, HTTPException, status
from app.schemas import TelemetryPayload, Diagnosis, ConditionProbability, SafetyTier, SeverityBand
from app.services.mock_generator import generate_mock_weather_context
from app.ml_engine.hydrology import calculate_et0_fao_56, evaluate_action_window
from app.ml_engine.crop_rf_model import crop_engine
from app.rag_engine.orchestrator import generate_farmer_advice

router = APIRouter(prefix="/copilot", tags=["AI Copilot Analysis"])

@router.post("/analyze", response_model=dict, status_code=status.HTTP_200_OK)
async def analyze_crop_health(payload: TelemetryPayload):
    """
    End-to-end analysis: Telemetry -> Hydrology -> ML Crop Prediction -> LLM Advice.
    """
    try:
        # 1. Hydrology Engine
        weather = generate_mock_weather_context(payload)
        weather.et0_fao = calculate_et0_fao_56(weather)
        action_window = evaluate_action_window(weather, payload.moisture_pct, crop_kc=1.1)
        weather.can_spray_today = action_window.can_spray_today

        # 2. Classical ML Crop Prediction & SHAP Explainability
        ml_prediction = crop_engine.predict_and_explain(payload.model_dump())

        # 3. Mock Vision/Diagnosis Engine (Simulating a GREEN tier for this MVP test)
        mock_diagnosis = Diagnosis(
            prediction_set=[
                ConditionProbability(
                    condition_id="wheat_yellow_rust",
                    probability=0.88,
                    is_in_conformal_set=True,
                )
            ],
            tier=SafetyTier.GREEN,
            severity=SeverityBand.MODERATE,
            symptoms_seen=["yellowish-orange pustules on upper leaf surface"],
            ood_score=0.12,
            model_versions={"vision_classifier": "v1.2.0"},
        )

        # 4. GenAI Orchestrator
        advice = generate_farmer_advice(
            diagnosis=mock_diagnosis,
            action_window=action_window,
            farmer_language="Urdu"
        )

        # 5. Return the complete, structured response
        return {
            "status": "success",
            "farm_id": payload.farm_id,
            "timestamp": payload.timestamp.isoformat(),
            "hydrology": {
                "et0_fao_mm_day": weather.et0_fao,
                "soil_moisture_pct": payload.moisture_pct,
            },
            "ml_prediction": ml_prediction,
            "diagnosis": mock_diagnosis.model_dump(),
            "advice": advice.model_dump(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Copilot analysis failed: {str(e)}"
        )