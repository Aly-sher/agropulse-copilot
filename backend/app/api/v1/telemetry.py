"""FastAPI endpoints for IoT telemetry ingestion and hydrology evaluation."""

from app.ml_engine.hydrology import calculate_et0_fao_56, evaluate_action_window
from app.schemas import TelemetryPayload
from app.services.mock_generator import generate_mock_telemetry, generate_mock_weather_context
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/telemetry", tags=["Telemetry & Hydrology"])

@router.post("/ingest", response_model=dict, status_code=status.HTTP_200_OK)
async def ingest_telemetry(payload: TelemetryPayload):
    """
    Ingests IoT telemetry, calculates FAO-56 ET0, and returns the safe action window.
    In production, this would also save to TimescaleDB.
    """
    try:
        # 1. Generate or receive weather context (Mocked for MVP)
        weather = generate_mock_weather_context(payload)

        # 2. Calculate Reference Evapotranspiration (ET0)
        et0 = calculate_et0_fao_56(weather)
        weather.et0_fao = et0

        # 3. Evaluate the safe action window based on weather and soil moisture
        action_window = evaluate_action_window(
            weather=weather,
            soil_moisture_pct=payload.moisture_pct,
            crop_kc=1.1  # Default crop coefficient for mid-season wheat
        )
        weather.can_spray_today = action_window.can_spray_today

        # 4. Return the consolidated response
        return {
            "status": "success",
            "farm_id": payload.farm_id,
            "timestamp": payload.timestamp.isoformat(),
            "hydrology": {
                "et0_fao_mm_day": et0,
                "soil_moisture_pct": payload.moisture_pct,
            },
            "action_window": action_window.model_dump(),
            "weather_context": weather.model_dump(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process telemetry: {str(e)}"
        )

@router.post("/mock", response_model=dict, status_code=status.HTTP_200_OK)
async def generate_and_ingest_mock():
    """Convenience endpoint to generate mock data and ingest it in one call."""
    mock_telemetry = generate_mock_telemetry()
    return await ingest_telemetry(mock_telemetry)
