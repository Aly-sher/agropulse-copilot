"""Classical ML and Hydrology Engine for AgroPulse Copilot."""

import math

from app.schemas import ActionWindow, WeatherContext

# Agronomic constants
WIND_SAFE_THRESHOLD_MS = 5.0  # Max safe wind speed for spraying (m/s)
MAX_RAIN_FORECAST_MM = 2.0    # Max forecasted rain to allow spraying (mm)

def calculate_et0_fao_56(weather: WeatherContext) -> float:
    """
    Simplified FAO-56 Penman-Monteith equation for Reference Evapotranspiration (ET0).
    Assumes standard atmospheric pressure at sea level for MVP simplicity.
    """
    T = weather.temp_c
    u2 = weather.wind_speed_ms
    RH = weather.relative_humidity_pct
    Rs = weather.solar_radiation_mj_m2

    # Saturation vapor pressure (kPa)
    es = 0.6108 * math.exp((17.27 * T) / (T + 237.3))

    # Actual vapor pressure (kPa)
    ea = (RH / 100.0) * es

    # Slope of vapor pressure curve (kPa/°C)
    delta = (4098.0 * es) / ((T + 237.3) ** 2)

    # Psychrometric constant (kPa/°C)
    gamma = 0.665e-3 * 101.3  # Simplified for sea level

    # Net radiation (simplified approximation from Rs)
    Rn = 0.77 * Rs - 2.45

    # Soil heat flux (G) assumed 0 for daily calculations
    G = 0.0

    # FAO-56 Penman-Monteith equation
    numerator = (0.408 * delta * (Rn - G)) + (gamma * (900 / (T + 273)) * u2 * (es - ea))
    denominator = delta + (gamma * (1 + 0.34 * u2))

    et0 = numerator / denominator
    return max(0.0, round(et0, 2))

def evaluate_action_window(weather: WeatherContext, soil_moisture_pct: float, crop_kc: float = 1.1) -> ActionWindow:
    """
    Determines the safe action window for irrigation and spraying based on weather and soil state.
    """
    # 1. Evaluate spraying safety
    can_spray = (weather.wind_speed_ms < WIND_SAFE_THRESHOLD_MS) and (weather.precipitation_mm < MAX_RAIN_FORECAST_MM)
    wind_warning = weather.wind_speed_ms >= WIND_SAFE_THRESHOLD_MS

    # 2. Calculate Crop Evapotranspiration (ETc = ET0 * Kc)
    etc = weather.et0_fao * crop_kc

    # 3. Simple soil moisture depletion logic
    # Assume field capacity is ~30%, wilting point is ~15%.
    # Irrigation is due if moisture drops below 20% and ETc is high.
    irrigation_due_hours = 0
    if soil_moisture_pct < 20.0 and etc > 3.0:
        irrigation_due_hours = 24  # Needs water within 24 hours
    elif soil_moisture_pct < 25.0:
        irrigation_due_hours = 48  # Monitor closely

    return ActionWindow(
        can_spray_today=can_spray,
        irrigation_due_hours=irrigation_due_hours,
        wind_warning=wind_warning
    )
