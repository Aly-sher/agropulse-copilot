"""Mock data generator for testing telemetry ingestion without physical IoT hardware."""

import random
from datetime import datetime

from app.schemas import TelemetryPayload, WeatherContext


def generate_mock_telemetry(farm_id: str = "farm_pk_001", node_id: str = "node_01") -> TelemetryPayload:
    """Generates realistic soil sensor data for a wheat field in Punjab."""
    return TelemetryPayload(
        timestamp=datetime.utcnow(),
        farm_id=farm_id,
        node_id=node_id,
        moisture_pct=random.uniform(15.0, 35.0),  # Volumetric water content (%)
        nitrogen_mg_kg=random.uniform(30.0, 60.0),
        phosphorus_mg_kg=random.uniform(15.0, 30.0),
        potassium_mg_kg=random.uniform(25.0, 45.0),
        ph=random.uniform(6.0, 8.0),  # Typical Punjab soil pH
        temp_c=random.uniform(18.0, 32.0),
    )

def generate_mock_weather_context(telemetry: TelemetryPayload) -> WeatherContext:
    """Generates realistic weather context matching the telemetry timestamp."""
    # Simulate a hot, dry day with moderate wind (common in pre-monsoon Punjab)
    temp_c = telemetry.temp_c + random.uniform(2.0, 5.0)  # Air temp is usually higher than soil temp
    wind_speed_ms = random.uniform(4.0, 7.0)  # Sometimes exceeds safe spray threshold (5.0)
    relative_humidity_pct = random.uniform(30.0, 50.0)
    solar_radiation_mj_m2 = random.uniform(18.0, 25.0)
    precipitation_mm = 0.0  # Dry season

    # We will calculate the actual ET0 in the API layer, so we pass a placeholder here
    # that the API will overwrite, or we can calculate it here for completeness.
    # For the mock, we'll let the API layer handle the hydrology calculation.

    return WeatherContext(
        timestamp=telemetry.timestamp,
        temp_c=temp_c,
        wind_speed_ms=wind_speed_ms,
        relative_humidity_pct=relative_humidity_pct,
        solar_radiation_mj_m2=solar_radiation_mj_m2,
        precipitation_mm=precipitation_mm,
        et0_fao=0.0,  # Placeholder, will be calculated by the hydrology engine
        can_spray_today=True,  # Placeholder, will be evaluated by the hydrology engine
    )
