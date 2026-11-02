"""Unit tests for the 6-Stage Computer Vision Pipeline."""

import numpy as np
import numpy as np
from PIL import Image, ImageFilter  # <-- Added ImageFilter here
import io
from app.ml_engine.leaf_vision_pipeline import stage0_quality_gate, stage4_conformal_and_ood
import io
from app.ml_engine.leaf_vision_pipeline import stage0_quality_gate, stage4_conformal_and_ood

def test_stage0_quality_gate_pass() -> None:
    """Test that a sharp, well-exposed image passes the quality gate."""
    # Create a 100x100 image with high contrast edges (sharp)
    img = Image.new("L", (100, 100), color=128)
    pixels = img.load()
    for i in range(0, 100, 2):
        for j in range(100):
            pixels[i, j] = 255 # High contrast
            
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    
    is_valid, reason, metrics = stage0_quality_gate(img_bytes.getvalue())
    
    assert is_valid is True
    # The image is half 128 and half 255, so mean brightness is 191.5
    assert metrics["brightness"] == 191.5

def test_stage0_quality_gate_fail_blur() -> None:
    """Test that a uniform (featureless/blurry) image fails the quality gate."""
    # Create a completely uniform gray image (zero features = zero laplacian variance)
    img = Image.new("L", (100, 100), color=128)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    
    is_valid, reason, metrics = stage0_quality_gate(img_bytes.getvalue())
    
    # It must fail, and the variance must be exactly 0.0 (which is < 80.0)
    assert is_valid is False
    assert metrics["laplacian_var"] == 0.0
    assert "blurry" in reason.lower()

def test_stage4_conformal_prediction_coverage() -> None:
    """Test that the Conformal Prediction Set includes the correct classes for 90% coverage."""
    # Logits that result in roughly [0.946, 0.047, 0.006] probabilities
    raw_logits = np.array([5.0, 2.0, 0.0])
    feature_vector = np.zeros(3)
    class_means = np.zeros((3, 3))
    class_covariances = np.eye(3)
    
    prediction_set, ood_score = stage4_conformal_and_ood(
        raw_logits, feature_vector, class_means, class_covariances, alpha=0.10
    )
    
    # With alpha=0.10, we need 90% coverage. 
    # The top class has ~0.946 prob, which is already >= 0.90.
    # So the set should contain exactly 1 class.
    assert len(prediction_set) == 1
    assert prediction_set[0].is_in_conformal_set is True
    assert prediction_set[0].probability > 0.90