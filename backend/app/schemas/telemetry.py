"""Strict data contracts for IoT telemetry and weather context."""

from datetime import datetime

from pydantic import BaseModel, Field


class TelemetryPayload(BaseModel):
    """Incoming payload from IoT soil sensors."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    farm_id: str = Field(..., description="Hashed farm identifier.")
    node_id: str = Field(..., description="Sensor node identifier.")

    # Soil metrics
    moisture_pct: float = Field(..., ge=0.0, le=100.0, description="Volumetric water content (%)")
    nitrogen_mg_kg: float = Field(..., ge=0.0, description="Nitrogen content (mg/kg)")
    phosphorus_mg_kg: float = Field(..., ge=0.0, description="Phosphorus content (mg/kg)")
    potassium_mg_kg: float = Field(..., ge=0.0, description="Potassium content (mg/kg)")
    ph: float = Field(..., ge=0.0, le=14.0, description="Soil pH")
    temp_c: float = Field(..., description="Soil temperature (Celsius)")

class WeatherContext(BaseModel):
    """Normalized weather and environmental context snapshot."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    temp_c: float = Field(..., description="Average air temperature (Celsius)")
    wind_speed_ms: float = Field(..., ge=0.0, description="Wind speed at 2m height (m/s)")
    relative_humidity_pct: float = Field(..., ge=0.0, le=100.0, description="Relative humidity (%)")
    solar_radiation_mj_m2: float = Field(..., ge=0.0, description="Solar radiation (MJ/m²/day)")
    precipitation_mm: float = Field(..., ge=0.0, description="Forecasted precipitation (mm)")

    # Derived agronomic features
    et0_fao: float = Field(..., ge=0.0, description="Reference evapotranspiration (mm/day) via FAO-56")
    can_spray_today: bool = Field(..., description="True if wind < safe threshold and no rain forecast")
