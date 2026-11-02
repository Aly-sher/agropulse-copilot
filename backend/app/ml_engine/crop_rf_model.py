"""Classical Tabular ML & SHAP Explainability Engine."""

import numpy as np
import shap
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier


class AgronomicRandomForestEngine:
    """
    Predicts optimal crop suitability and explains the decision using SHAP.
    In production, the model would be loaded from a .joblib file. 
    For this MVP, it trains on synthetic agronomic data on initialization.
    """
    def __init__(self):
        self.feature_names = ["nitrogen", "phosphorus", "potassium", "moisture", "ph", "temp"]
        self.target_names = ["Wheat", "Rice", "Maize", "Cotton"]

        # Initialize and train on synthetic data (Replace with joblib.load in prod)
        self.model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
        self._train_synthetic_baseline()

        # Initialize SHAP TreeExplainer
        self.explainer = shap.TreeExplainer(self.model)

    def _train_synthetic_baseline(self) -> None:
        """Trains a baseline model on synthetic data to prove the SHAP pipeline works."""
        X, y = make_classification(
            n_samples=1000, n_features=6, n_classes=4,
            n_informative=4, random_state=42
        )
        self.model.fit(X, y)

    def predict_and_explain(self, telemetry: dict) -> dict:
        """
        Takes raw telemetry, predicts the best crop, and returns SHAP feature attributions.
        """
        # Extract features in the exact order the model expects
        features = [
            telemetry.get("nitrogen_mg_kg", 0),
            telemetry.get("phosphorus_mg_kg", 0),
            telemetry.get("potassium_mg_kg", 0),
            telemetry.get("moisture_pct", 0),
            telemetry.get("ph", 0),
            telemetry.get("temp_c", 0)
        ]

        X = np.array([features])

        # 1. Get Prediction and Probabilities
        prediction_idx = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]

        # 2. Calculate SHAP values
        shap_values = self.explainer.shap_values(X)

        # Handle SHAP output format (list of arrays for multi-class)
        if isinstance(shap_values, list):
            predicted_class_shap = shap_values[prediction_idx][0]
        else:
            predicted_class_shap = shap_values[0]

        # Map SHAP values to feature names
        feature_importance = {
            name: float(round(val, 4))
            for name, val in zip(self.feature_names, predicted_class_shap)
        }

        return {
            "predicted_crop": self.target_names[prediction_idx],
            "confidence_pct": float(round(max(probabilities) * 100, 2)),
            "shap_explanation": feature_importance
        }

# Singleton instance for the API to use
crop_engine = AgronomicRandomForestEngine()
