"""Production ML inference service for PAIMANA risk engine.

Loads trained v2 models (XGBoost cost, LightGBM schedule) and provides
prediction capabilities with proper feature engineering, one-hot encoding,
and SHAP explainability.

Models:
- XGBoost v2: cost_overrun_10pct (Test ROC-AUC: 0.809)
- LightGBM v2: delay_gt_6_months (Test ROC-AUC: 0.757)

Features:
- Numerical: completion_by_expenditure, completion_by_progress, log_sanctioned_cost, cost_revision_ratio
- One-hot: sector (10-11 categories), size_band (5 categories), state (10 categories)
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# Model paths - resolve relative to project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
MODEL_DIR = PROJECT_ROOT / "data" / "artifacts" / "experimental" / "v2"
COST_MODEL_PATH = MODEL_DIR / "xgboost_cost_v2.pkl"
SCHEDULE_MODEL_PATH = MODEL_DIR / "lightgbm_schedule_v2.pkl"
COST_FEATURES_PATH = MODEL_DIR / "cost_feature_names_v2.json"
SCHEDULE_FEATURES_PATH = MODEL_DIR / "schedule_feature_names_v2.json"

# Size band thresholds (from rcf_engine.py)
SIZE_BANDS = {
    "SMALL": (150, 500),
    "MEDIUM": (500, 2000),
    "LARGE": (2000, float("inf")),
    "XLARGE": (float("inf"), float("inf")),  # For very large projects
}


@dataclass(frozen=True)
class MLPredictionResult:
    """Result of ML prediction."""
    model_id: str
    model_name: str
    model_version: str
    target: str
    probability: float
    predicted_class: int
    shap_drivers: Optional[List[Dict]]
    feature_values: Dict[str, float]
    inference_timestamp: datetime
    status: str
    error: Optional[str] = None


@dataclass(frozen=True)
class FeatureEngineeringResult:
    """Result of feature engineering."""
    features: Dict[str, float]
    one_hot_features: Dict[str, float]
    feature_vector: np.ndarray
    feature_names: List[str]
    missing_features: List[str]
    status: str


class ProductionMLInferenceService:
    """Production ML inference service with proper feature engineering."""

    def __init__(self, model_dir: Optional[Path] = None):
        """Initialize ML inference service.
        
        Args:
            model_dir: Path to model directory (defaults to MODEL_DIR)
        """
        self.model_dir = model_dir or MODEL_DIR
        self.cost_model = None
        self.schedule_model = None
        self.cost_feature_names = []
        self.schedule_feature_names = []
        self._load_models()

    def _load_models(self):
        """Load trained models and feature names."""
        try:
            # Load cost model
            if COST_MODEL_PATH.exists():
                self.cost_model = joblib.load(COST_MODEL_PATH)
                logger.info(f"Loaded cost model from {COST_MODEL_PATH}")
            else:
                logger.warning(f"Cost model not found at {COST_MODEL_PATH}")

            # Load schedule model
            if SCHEDULE_MODEL_PATH.exists():
                self.schedule_model = joblib.load(SCHEDULE_MODEL_PATH)
                logger.info(f"Loaded schedule model from {SCHEDULE_MODEL_PATH}")
            else:
                logger.warning(f"Schedule model not found at {SCHEDULE_MODEL_PATH}")

            # Load feature names
            if COST_FEATURES_PATH.exists():
                with open(COST_FEATURES_PATH, "r") as f:
                    self.cost_feature_names = json.load(f)
                logger.info(f"Loaded {len(self.cost_feature_names)} cost feature names")
            else:
                logger.warning(f"Cost feature names not found at {COST_FEATURES_PATH}")

            if SCHEDULE_FEATURES_PATH.exists():
                with open(SCHEDULE_FEATURES_PATH, "r") as f:
                    self.schedule_feature_names = json.load(f)
                logger.info(f"Loaded {len(self.schedule_feature_names)} schedule feature names")
            else:
                logger.warning(f"Schedule feature names not found at {SCHEDULE_FEATURES_PATH}")

        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self.cost_model = None
            self.schedule_model = None

    def _get_size_band(self, sanctioned_cost: float) -> str:
        """Get size band from sanctioned cost."""
        if sanctioned_cost < 500:
            return "SMALL"
        elif sanctioned_cost < 2000:
            return "MEDIUM"
        elif sanctioned_cost < 5000:
            return "LARGE"
        else:
            return "XLARGE"

    def _engineer_features(
        self,
        project: Dict,
        submission: Dict,
    ) -> FeatureEngineeringResult:
        """Engineer features from project and submission data.
        
        Args:
            project: Project dict with sector, state, sanctioned_cost, approved_date
            submission: Submission dict with revised_cost, expenditure, physical_progress, planned_completion
        
        Returns:
            FeatureEngineeringResult with engineered features
        """
        try:
            # Extract numeric values safely
            sanctioned_cost = float(project.get("sanctioned_cost", 0) or 0)
            revised_cost = float(submission.get("revised_cost", 0) or 0)
            expenditure = float(submission.get("expenditure", 0) or 0)
            physical_progress = float(submission.get("physical_progress", 0) or 0)

            # Handle division by zero
            completion_by_expenditure = (
                expenditure / sanctioned_cost if sanctioned_cost > 0 else 0.0
            )
            completion_by_progress = physical_progress / 100.0 if physical_progress > 0 else 0.0
            log_sanctioned_cost = (
                math.log(sanctioned_cost) if sanctioned_cost > 0 else 0.0
            )
            cost_revision_ratio = (
                revised_cost / sanctioned_cost if sanctioned_cost > 0 else 1.0
            )

            # Base numerical features
            features = {
                "completion_by_expenditure": completion_by_expenditure,
                "completion_by_progress": completion_by_progress,
                "log_sanctioned_cost": log_sanctioned_cost,
                "cost_revision_ratio": cost_revision_ratio,
            }

            # One-hot encoding
            sector = project.get("sector", "Unknown")
            state = project.get("state", "Unknown")
            size_band = self._get_size_band(sanctioned_cost)

            one_hot_features = {}
            
            # Sector one-hot
            sector_prefix = "sector_"
            for feature_name in self.cost_feature_names + self.schedule_feature_names:
                if feature_name.startswith(sector_prefix):
                    sector_name = feature_name.replace(sector_prefix, "")
                    one_hot_features[feature_name] = 1.0 if sector == sector_name else 0.0

            # Size band one-hot
            size_prefix = "size_band_"
            for feature_name in self.cost_feature_names + self.schedule_feature_names:
                if feature_name.startswith(size_prefix):
                    band_name = feature_name.replace(size_prefix, "")
                    one_hot_features[feature_name] = 1.0 if size_band == band_name else 0.0

            # State one-hot
            state_prefix = "state_"
            for feature_name in self.cost_feature_names + self.schedule_feature_names:
                if feature_name.startswith(state_prefix):
                    state_name = feature_name.replace(state_prefix, "")
                    one_hot_features[feature_name] = 1.0 if state == state_name else 0.0

            # Combine features
            all_features = {**features, **one_hot_features}

            # Check for missing features
            missing_features = []
            for feature_name in self.cost_feature_names + self.schedule_feature_names:
                if feature_name not in all_features:
                    missing_features.append(feature_name)
                    all_features[feature_name] = 0.0

            return FeatureEngineeringResult(
                features=features,
                one_hot_features=one_hot_features,
                feature_vector=np.array([all_features.get(f, 0.0) for f in self.cost_feature_names]),
                feature_names=self.cost_feature_names,
                missing_features=missing_features,
                status="success" if not missing_features else "partial",
            )

        except Exception as e:
            logger.error(f"Feature engineering failed: {e}")
            return FeatureEngineeringResult(
                features={},
                one_hot_features={},
                feature_vector=np.array([]),
                feature_names=[],
                missing_features=[],
                status="error",
            )

    def predict_cost_risk(
        self,
        project: Dict,
        submission: Dict,
        use_shap: bool = True,
    ) -> MLPredictionResult:
        """Predict cost overrun risk using XGBoost v2 model.
        
        Args:
            project: Project dict with sector, state, sanctioned_cost
            submission: Submission dict with revised_cost, expenditure, physical_progress
            use_shap: Whether to generate SHAP explanations
        
        Returns:
            MLPredictionResult with prediction and SHAP drivers
        """
        if self.cost_model is None:
            return MLPredictionResult(
                model_id="xgboost_cost_v2",
                model_name="XGBoost Cost Overrun v2",
                model_version="2.0",
                target="cost_overrun_10pct",
                probability=0.0,
                predicted_class=0,
                shap_drivers=None,
                feature_values={},
                inference_timestamp=datetime.utcnow(),
                status="unavailable",
                error="Cost model not loaded",
            )

        try:
            # Engineer features
            fe_result = self._engineer_features(project, submission)
            
            if fe_result.status == "error":
                return MLPredictionResult(
                    model_id="xgboost_cost_v2",
                    model_name="XGBoost Cost Overrun v2",
                    model_version="2.0",
                    target="cost_overrun_10pct",
                    probability=0.0,
                    predicted_class=0,
                    shap_drivers=None,
                    feature_values={},
                    inference_timestamp=datetime.utcnow(),
                    status="error",
                    error="Feature engineering failed",
                )

            # Build feature vector for cost model
            cost_feature_vector = np.array(
                [fe_result.features.get(f, 0.0) if not f.startswith(("sector_", "state_", "size_band_"))
                 else fe_result.one_hot_features.get(f, 0.0)
                 for f in self.cost_feature_names]
            ).reshape(1, -1)

            # Predict
            y_pred = self.cost_model.predict(cost_feature_vector)[0]
            y_proba = self.cost_model.predict_proba(cost_feature_vector)[0, 1]

            # SHAP explanation
            shap_drivers = None
            if use_shap:
                try:
                    import shap
                    explainer = shap.TreeExplainer(self.cost_model)
                    shap_values = explainer.shap_values(cost_feature_vector)
                    
                    # Handle different SHAP output formats
                    if isinstance(shap_values, list):
                        shap_values = shap_values[0]
                    
                    # Get top 5 features by absolute SHAP value
                    abs_shap = np.abs(shap_values[0])
                    top_indices = np.argsort(abs_shap)[-5:][::-1]
                    
                    shap_drivers = []
                    for idx in top_indices:
                        fname = self.cost_feature_names[idx]
                        fvalue = cost_feature_vector[0, idx]
                        shap_val = shap_values[0, idx]
                        
                        shap_drivers.append({
                            "feature": fname,
                            "value": float(fvalue),
                            "contribution": float(shap_val),
                            "direction": "increases_risk" if shap_val > 0 else "decreases_risk",
                        })
                except ImportError:
                    logger.warning("SHAP not available")
                except Exception as e:
                    logger.error(f"SHAP generation failed: {e}")

            return MLPredictionResult(
                model_id="xgboost_cost_v2",
                model_name="XGBoost Cost Overrun v2",
                model_version="2.0",
                target="cost_overrun_10pct",
                probability=float(y_proba),
                predicted_class=int(y_pred),
                shap_drivers=shap_drivers,
                feature_values=fe_result.features,
                inference_timestamp=datetime.utcnow(),
                status="success",
            )

        except Exception as e:
            logger.error(f"Cost prediction failed: {e}")
            return MLPredictionResult(
                model_id="xgboost_cost_v2",
                model_name="XGBoost Cost Overrun v2",
                model_version="2.0",
                target="cost_overrun_10pct",
                probability=0.0,
                predicted_class=0,
                shap_drivers=None,
                feature_values={},
                inference_timestamp=datetime.utcnow(),
                status="error",
                error=str(e),
            )

    def predict_schedule_risk(
        self,
        project: Dict,
        submission: Dict,
        use_shap: bool = True,
    ) -> MLPredictionResult:
        """Predict schedule delay risk using LightGBM v2 model.
        
        Args:
            project: Project dict with sector, state, sanctioned_cost
            submission: Submission dict with revised_cost, expenditure, physical_progress
            use_shap: Whether to generate SHAP explanations
        
        Returns:
            MLPredictionResult with prediction and SHAP drivers
        """
        if self.schedule_model is None:
            return MLPredictionResult(
                model_id="lightgbm_schedule_v2",
                model_name="LightGBM Schedule Delay v2",
                model_version="2.0",
                target="delay_gt_6_months",
                probability=0.0,
                predicted_class=0,
                shap_drivers=None,
                feature_values={},
                inference_timestamp=datetime.utcnow(),
                status="unavailable",
                error="Schedule model not loaded",
            )

        try:
            # Engineer features
            fe_result = self._engineer_features(project, submission)
            
            if fe_result.status == "error":
                return MLPredictionResult(
                    model_id="lightgbm_schedule_v2",
                    model_name="LightGBM Schedule Delay v2",
                    model_version="2.0",
                    target="delay_gt_6_months",
                    probability=0.0,
                    predicted_class=0,
                    shap_drivers=None,
                    feature_values={},
                    inference_timestamp=datetime.utcnow(),
                    status="error",
                    error="Feature engineering failed",
                )

            # Build feature vector for schedule model
            schedule_feature_vector = np.array(
                [fe_result.features.get(f, 0.0) if not f.startswith(("sector_", "state_", "size_band_"))
                 else fe_result.one_hot_features.get(f, 0.0)
                 for f in self.schedule_feature_names]
            ).reshape(1, -1)

            # Predict
            y_pred = self.schedule_model.predict(schedule_feature_vector)[0]
            y_proba = self.schedule_model.predict_proba(schedule_feature_vector)[0, 1]

            # SHAP explanation
            shap_drivers = None
            if use_shap:
                try:
                    import shap
                    explainer = shap.TreeExplainer(self.schedule_model)
                    shap_values = explainer.shap_values(schedule_feature_vector)
                    
                    # Handle different SHAP output formats
                    if isinstance(shap_values, list):
                        shap_values = shap_values[0]
                    
                    # Get top 5 features by absolute SHAP value
                    abs_shap = np.abs(shap_values[0])
                    top_indices = np.argsort(abs_shap)[-5:][::-1]
                    
                    shap_drivers = []
                    for idx in top_indices:
                        fname = self.schedule_feature_names[idx]
                        fvalue = schedule_feature_vector[0, idx]
                        shap_val = shap_values[0, idx]
                        
                        shap_drivers.append({
                            "feature": fname,
                            "value": float(fvalue),
                            "contribution": float(shap_val),
                            "direction": "increases_risk" if shap_val > 0 else "decreases_risk",
                        })
                except ImportError:
                    logger.warning("SHAP not available")
                except Exception as e:
                    logger.error(f"SHAP generation failed: {e}")

            return MLPredictionResult(
                model_id="lightgbm_schedule_v2",
                model_name="LightGBM Schedule Delay v2",
                model_version="2.0",
                target="delay_gt_6_months",
                probability=float(y_proba),
                predicted_class=int(y_pred),
                shap_drivers=shap_drivers,
                feature_values=fe_result.features,
                inference_timestamp=datetime.utcnow(),
                status="success",
            )

        except Exception as e:
            logger.error(f"Schedule prediction failed: {e}")
            return MLPredictionResult(
                model_id="lightgbm_schedule_v2",
                model_name="LightGBM Schedule Delay v2",
                model_version="2.0",
                target="delay_gt_6_months",
                probability=0.0,
                predicted_class=0,
                shap_drivers=None,
                feature_values={},
                inference_timestamp=datetime.utcnow(),
                status="error",
                error=str(e),
            )

    def is_available(self) -> bool:
        """Check if ML models are available."""
        return self.cost_model is not None or self.schedule_model is not None

    def get_model_info(self) -> Dict:
        """Get information about loaded models."""
        return {
            "cost_model": {
                "loaded": self.cost_model is not None,
                "path": str(COST_MODEL_PATH),
                "feature_count": len(self.cost_feature_names),
            },
            "schedule_model": {
                "loaded": self.schedule_model is not None,
                "path": str(SCHEDULE_MODEL_PATH),
                "feature_count": len(self.schedule_feature_names),
            },
        }


# Global singleton instance
_ml_inference_service: Optional[ProductionMLInferenceService] = None


def get_ml_inference_service() -> ProductionMLInferenceService:
    """Get global ML inference service instance (singleton pattern)."""
    global _ml_inference_service
    if _ml_inference_service is None:
        _ml_inference_service = ProductionMLInferenceService()
    return _ml_inference_service
