"""Statistical anomaly detection for IoT telemetry using Rolling Z-Score."""

from collections import deque

import numpy as np


class ZScoreAnomalyFilter:
    """
    Detects sensor spikes or disconnections using a rolling standard deviation.
    Prevents bad data from corrupting the ML models.
    """
    def __init__(self, window_size: int = 10, threshold: float = 3.0):
        self.window_size = window_size
        self.threshold = threshold
        # Deque automatically drops old data when it exceeds maxlen
        self.history = deque(maxlen=window_size)

    def evaluate(self, value: float) -> dict:
        """Evaluates a single sensor reading against the rolling history."""
        self.history.append(value)

        # Need at least 2 points to calculate standard deviation
        if len(self.history) < 2:
            return {"is_anomaly": False, "z_score": 0.0, "value": value}

        arr = np.array(self.history)
        mean = np.mean(arr)
        std = np.std(arr)

        # Prevent division by zero if all values in the window are identical
        if std == 0:
            z_score = 0.0
        else:
            z_score = abs((value - mean) / std)

        return {
            "is_anomaly": bool(z_score > self.threshold),
            "z_score": float(round(z_score, 4)),
            "value": float(value)
        }
