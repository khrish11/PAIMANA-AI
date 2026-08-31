"""Model loading service for experimental PAIMANA ML models.

Loads and caches experimental ML models at startup.
"""

import joblib
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """Load and cache experimental ML models."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.models: Dict[str, Dict] = {}
        self._load_models()
    
    def _load_models(self):
        """Load all experimental models at startup."""
        artifact_dir = self.data_dir / 'artifacts' / 'experimental'
        
        model_configs = [
            {
                'model_type': 'random_forest',
                'version': 'rf-exp-v1',
                'artifact': 'random_forest_experimental.pkl',
                'target': 'delay_gt_6_months',
                'feature_version': 'v1'
            },
            {
                'model_type': 'xgboost',
                'version': 'xgb-exp-v1',
                'artifact': 'xgboost_experimental.pkl',
                'target': 'delay_gt_6_months',
                'feature_version': 'v1'
            },
            {
                'model_type': 'lightgbm',
                'version': 'lgb-exp-v1',
                'artifact': 'lightgbm_experimental.pkl',
                'target': 'delay_gt_6_months',
                'feature_version': 'v1'
            }
        ]
        
        for config in model_configs:
            artifact_path = artifact_dir / config['artifact']
            
            if artifact_path.exists():
                try:
                    model = joblib.load(artifact_path)
                    self.models[config['model_type']] = {
                        'model': model,
                        'version': config['version'],
                        'status': 'experimental',
                        'target': config['target'],
                        'feature_version': config['feature_version'],
                        'loaded': True
                    }
                    logger.info(f"Loaded {config['model_type']} model: {config['version']}")
                except Exception as e:
                    logger.error(f"Failed to load {config['model_type']}: {e}")
                    self.models[config['model_type']] = {
                        'model': None,
                        'version': config['version'],
                        'status': 'unavailable',
                        'target': config['target'],
                        'feature_version': config['feature_version'],
                        'loaded': False,
                        'error': str(e)
                    }
            else:
                logger.warning(f"Model artifact not found: {artifact_path}")
                self.models[config['model_type']] = {
                    'model': None,
                    'version': config['version'],
                    'status': 'unavailable',
                    'target': config['target'],
                    'feature_version': config['feature_version'],
                    'loaded': False,
                    'error': 'Artifact not found'
                }
    
    def get_model(self, model_type: str) -> Optional[Dict]:
        """Get model by type."""
        return self.models.get(model_type)
    
    def get_available_models(self) -> Dict[str, Dict]:
        """Get all available models."""
        return self.models
    
    def is_model_available(self, model_type: str) -> bool:
        """Check if model is available."""
        model_info = self.models.get(model_type)
        return model_info is not None and model_info.get('loaded', False)


# Global model loader instance
_model_loader: Optional[ModelLoader] = None


def get_model_loader() -> ModelLoader:
    """Get global model loader instance."""
    global _model_loader
    if _model_loader is None:
        from backend.app.core.config import settings
        data_dir = Path(settings.DATA_DIR)
        _model_loader = ModelLoader(data_dir)
    return _model_loader


def initialize_model_loader(data_dir: Path):
    """Initialize model loader with data directory."""
    global _model_loader
    _model_loader = ModelLoader(data_dir)
