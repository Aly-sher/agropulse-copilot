"""Unit tests for the Classical ML and Hydrology Engine."""

from datetime import datetime

from app.ml_engine.hydrology import calculate_et0_fao_56, evaluate_action_window
from app.schemas import TelemetryPayload, WeatherContext


def test_calculate_et0_fao_56_normal_conditions() -> None:
    """Test ET0 calculation under standard, healthy crop conditions."""
    weather = WeatherContext(
        timestamp=datetime.utcnow(),
        temp_c=25.0,
        wind_speed_ms=2.0,
        relative_humidity_pct=60.0,
        solar_radiation_mj_m2=20.0,
        precipitation_mm=0.0,
        et0_fao=0.0,  # Placeholder, will be calculated
        can_spray_today=True,
    )

    et0 = calculate_et0_fao_56(weather)
    # For 25C, 60% RH, 2m/s wind, 20MJ radiation, ET0 should be roughly 4.5 - 5.5 mm/day
    assert 4.0 <= et0 <= 6.0

def test_evaluate_action_window_safe_to_spray() -> None:
    """Test that spraying is allowed when wind is low and no rain is forecast."""
    weather = WeatherContext(
        timestamp=datetime.utcnow(),
        temp_c=22.0,
        wind_speed_ms=3.0,  # Below 5.0 m/s threshold
        relative_humidity_pct=50.0,
        solar_radiation_mj_m2=18.0,
        precipitation_mm=0.0,  # No rain
        et0_fao=4.5,
        can_spray_today=True,
    )

    telemetry = TelemetryPayload(
        timestamp=datetime.utcnow(),
        farm_id="farm_123",
        node_id="node_1",
        moisture_pct=28.0,
        nitrogen_mg_kg=40.0,
        phosphorus_mg_kg=20.0,
        potassium_mg_kg=30.0,
        ph=6.5,
        temp_c=22.0,
    )

    action_window = evaluate_action_window(weather, telemetry.moisture_pct)

    assert action_window.can_spray_today is True
    assert action_window.wind_warning is False
    assert action_window.irrigation_due_hours == 0  # Moisture is healthy (28%)

def test_evaluate_action_window_wind_warning_and_irrigation_due() -> None:
    """Test that high wind triggers a warning and low moisture triggers irrigation."""
    weather = WeatherContext(
        timestamp=datetime.utcnow(),
        temp_c=30.0,
        wind_speed_ms=6.5,  # Above 5.0 m/s threshold
        relative_humidity_pct=40.0,
        solar_radiation_mj_m2=25.0,
        precipitation_mm=0.0,
        et0_fao=6.0,  # High evapotranspiration
        can_spray_today=True,
    )

    telemetry = TelemetryPayload(
        timestamp=datetime.utcnow(),
        farm_id="farm_123",
        node_id="node_1",
        moisture_pct=18.0,  # Below 20% threshold
        nitrogen_mg_kg=40.0,
        phosphorus_mg_kg=20.0,
        potassium_mg_kg=30.0,
        ph=6.5,
        temp_c=30.0,
    )

    action_window = evaluate_action_window(weather, telemetry.moisture_pct, crop_kc=1.2)

    assert action_window.can_spray_today is False  # Wind too high
    assert action_window.wind_warning is True
    assert action_window.irrigation_due_hours == 24  # Critical moisture + high ETc
