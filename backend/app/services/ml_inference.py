"""ML inference service for experimental PAIMANA models.

Provides prediction functions for cost and schedule risk.
"""

import numpy as np
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class MLInferenceService:
    """ML inference service for experimental models."""
    
    def __init__(self, model_loader):
        self.model_loader = model_loader
        self.feature_names = [
            'original_cost_crore', 'revised_cost_crore', 
            'cumulative_expenditure_crore', 'physical_progress_pct'
        ]
    
    def _extract_features(self, project_data: Dict) -> np.ndarray:
        """Extract features from project data."""
        features = []
        for fname in self.feature_names:
            val = project_data.get(fname)
            try:
                features.append(float(val) if val else 0.0)
            except (ValueError, TypeError):
                features.append(0.0)
        return np.array([features])
    
    def predict_with_model(self, model_type: str, project_data: Dict) -> Dict:
        """Predict using specified model."""
        model_info = self.model_loader.get_model(model_type)
        
        if not model_info or not model_info.get('loaded'):
            return {
                'model_type': model_type,
                'status': 'unavailable',
                'error': model_info.get('error', 'Model not loaded') if model_info else 'Model not found'
            }
        
        try:
            model = model_info['model']
            X = self._extract_features(project_data)
            
            # Get prediction
            y_pred = model.predict(X)[0]
            y_proba = model.predict_proba(X)[0, 1] if hasattr(model, 'predict_proba') else float(y_pred)
            
            return {
                'model_type': model_type,
                'model_version': model_info['version'],
                'status': model_info['status'],
                'target': model_info['target'],
                'feature_version': model_info['feature_version'],
                'probability': float(y_proba),
                'predicted_class': int(y_pred)
            }
        except Exception as e:
            logger.error(f"Prediction failed for {model_type}: {e}")
            return {
                'model_type': model_type,
                'status': 'error',
                'error': str(e)
            }
    
    def predict_cost_risk(self, project_data: Dict) -> Dict:
        """Predict cost risk using experimental models."""
        # Use XGBoost as primary model for cost risk
        return self.predict_with_model('xgboost', project_data)
    
    def predict_schedule_risk(self, project_data: Dict) -> Dict:
        """Predict schedule risk using experimental models."""
        # Use XGBoost as primary model for schedule risk
        return self.predict_with_model('xgboost', project_data)
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get all available models."""
        return self.model_loader.get_available_models()


# Global inference service instance
_inference_service: Optional[MLInferenceService] = None


def get_inference_service() -> MLInferenceService:
    """Get global inference service instance."""
    global _inference_service
    if _inference_service is None:
        from backend.app.services.model_loader import get_model_loader
        model_loader = get_model_loader()
        _inference_service = MLInferenceService(model_loader)
    return _inference_service
