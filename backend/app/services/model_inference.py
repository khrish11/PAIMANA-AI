"""Real ML inference service using trained model artifacts."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class ModelInferenceService:
    """Service for real ML inference using trained artifacts."""
    
    def __init__(self, model_loader):
        self.model_loader = model_loader
        self.feature_names = self._load_feature_names()
    
    def _load_feature_names(self) -> List[str]:
        """Load feature names from artifacts."""
        feature_file = Path(self.model_loader.data_dir) / 'artifacts' / 'experimental' / 'feature_names.json'
        if feature_file.exists():
            with open(feature_file) as f:
                return json.load(f)
        return []
    
    def prepare_features(self, project_data: Dict) -> Optional[np.ndarray]:
        """Prepare features for ML inference.
        
        Maps database fields to trained model feature names:
        - original_cost_crore <- sanctioned_cost
        - revised_cost_crore <- revised_cost (from latest submission)
        - cumulative_expenditure_crore <- expenditure (from latest submission)
        - physical_progress_pct <- physical_progress (from latest submission)
        """
        try:
            # Map database fields to model features
            feature_mapping = {
                'original_cost_crore': project_data.get('sanctioned_cost', 0),
                'revised_cost_crore': project_data.get('revised_cost', project_data.get('sanctioned_cost', 0)),
                'cumulative_expenditure_crore': project_data.get('expenditure', 0),
                'physical_progress_pct': project_data.get('physical_progress', 0)
            }
            
            # Extract features according to trained model schema
            features = []
            for feature_name in self.feature_names:
                if feature_name in feature_mapping:
                    value = feature_mapping[feature_name]
                    if value is None:
                        logger.warning(f"Feature {feature_name} is None, using 0")
                        value = 0.0
                    features.append(float(value))
                else:
                    logger.warning(f"Feature {feature_name} not found in feature mapping")
                    return None
            
            return np.array(features).reshape(1, -1)
        except Exception as e:
            logger.error(f"Feature preparation failed: {e}")
            return None
    
    def predict(self, model_type: str, project_data: Dict) -> Optional[Dict]:
        """Make prediction using trained model."""
        model_info = self.model_loader.get_model(model_type)
        
        if not model_info or not model_info.get('loaded'):
            return {
                'status': 'unavailable',
                'error': model_info.get('error', 'Model not loaded') if model_info else 'Model not found'
            }
        
        model = model_info['model']
        
        # Prepare features
        features = self.prepare_features(project_data)
        if features is None:
            return {
                'status': 'unavailable',
                'error': 'Feature preparation failed - required features missing'
            }
        
        try:
            # Get prediction
            if hasattr(model, 'predict_proba'):
                proba = model.predict_proba(features)[0]
                prediction = model.predict(features)[0]
                probability = proba[1] if len(proba) > 1 else proba[0]
            else:
                prediction = model.predict(features)[0]
                probability = float(prediction)
            
            return {
                'status': 'success',
                'model_type': model_type,
                'model_version': model_info['version'],
                'model_status': model_info['status'],
                'target': model_info['target'],
                'predicted_probability': float(probability),
                'predicted_class': int(prediction),
                'feature_version': model_info['feature_version']
            }
        except Exception as e:
            logger.error(f"Prediction failed for {model_type}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get status of all available models."""
        return self.model_loader.get_available_models()


def get_inference_service() -> Optional[ModelInferenceService]:
    """Get global inference service instance."""
    from app.services.model_loader import get_model_loader
    model_loader = get_model_loader()
    if model_loader:
        return ModelInferenceService(model_loader)
    return None
