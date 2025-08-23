"""
NQH2O Prediction API Routes
Provides endpoints for water index forecasting using trained ML models
"""

import os
import sys
import numpy as np
import pandas as pd
import joblib
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

prediction_bp = Blueprint('prediction', __name__)

class NQH2OPredictor:
    """
    NQH2O prediction service using trained ML models
    """
    
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = None
        self.feature_selector = None
        self.ensemble_weights = {}
        self.feature_names = []
        self.is_loaded = False
        
    def load_models(self):
        """Load all trained models and preprocessing objects"""
        try:
            logger.info("Loading NQH2O prediction models...")
            
            # Load individual models
            model_files = {
                'ridge': 'nqh2o_model_ridge.joblib',
                'lasso': 'nqh2o_model_lasso.joblib',
                'elastic_net': 'nqh2o_model_elastic_net.joblib',
                'random_forest': 'nqh2o_model_random_forest.joblib',
                'gradient_boosting': 'nqh2o_model_gradient_boosting.joblib'
            }
            
            for model_name, filename in model_files.items():
                filepath = os.path.join(self.model_dir, filename)
                if os.path.exists(filepath):
                    self.models[model_name] = joblib.load(filepath)
                    logger.info(f"✓ Loaded {model_name} model")
                else:
                    logger.warning(f"✗ Model file not found: {filepath}")
            
            # Load preprocessing objects
            scalers_path = os.path.join(self.model_dir, 'nqh2o_scalers.joblib')
            if os.path.exists(scalers_path):
                self.scalers = joblib.load(scalers_path)
                logger.info("✓ Loaded scalers")
            
            selector_path = os.path.join(self.model_dir, 'nqh2o_feature_selector.joblib')
            if os.path.exists(selector_path):
                self.feature_selector = joblib.load(selector_path)
                logger.info("✓ Loaded feature selector")
            
            weights_path = os.path.join(self.model_dir, 'nqh2o_ensemble_weights.joblib')
            if os.path.exists(weights_path):
                self.ensemble_weights = joblib.load(weights_path)
                logger.info("✓ Loaded ensemble weights")
            
            # Load feature names
            names_path = os.path.join(self.model_dir, 'nqh2o_feature_names.txt')
            if os.path.exists(names_path):
                with open(names_path, 'r') as f:
                    self.feature_names = [line.strip() for line in f.readlines()]
                logger.info(f"✓ Loaded {len(self.feature_names)} feature names")
            
            self.is_loaded = True
            logger.info(f"✓ All models loaded successfully. Available models: {list(self.models.keys())}")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            self.is_loaded = False
            raise
    
    def preprocess_features(self, features_dict):
        """Preprocess input features for prediction"""
        try:
            # Convert to DataFrame
            df = pd.DataFrame([features_dict])
            
            # Ensure all required features are present
            missing_features = set(self.feature_names) - set(df.columns)
            if missing_features:
                # Fill missing features with 0 (or could use mean/median)
                for feature in missing_features:
                    df[feature] = 0.0
                logger.warning(f"Missing features filled with 0: {missing_features}")
            
            # Select only the required features in correct order
            df = df[self.feature_names]
            
            # Apply scaling
            if self.scalers and 'standard' in self.scalers:
                scaled_features = self.scalers['standard'].transform(df)
            else:
                scaled_features = df.values
            
            # Apply feature selection
            if self.feature_selector:
                selected_features = self.feature_selector.transform(scaled_features)
            else:
                selected_features = scaled_features
            
            return selected_features
            
        except Exception as e:
            logger.error(f"Error preprocessing features: {str(e)}")
            raise
    
    def predict(self, features_dict, model_name='ensemble'):
        """Make prediction using specified model or ensemble"""
        try:
            if not self.is_loaded:
                raise ValueError("Models not loaded. Call load_models() first.")
            
            # Preprocess features
            processed_features = self.preprocess_features(features_dict)
            
            if model_name == 'ensemble':
                # Ensemble prediction
                predictions = {}
                for name, model in self.models.items():
                    pred = model.predict(processed_features)[0]
                    predictions[name] = pred
                
                # Weighted ensemble
                ensemble_pred = 0.0
                total_weight = 0.0
                for name, pred in predictions.items():
                    weight = self.ensemble_weights.get(name, 1.0 / len(predictions))
                    ensemble_pred += weight * pred
                    total_weight += weight
                
                if total_weight > 0:
                    ensemble_pred /= total_weight
                
                return {
                    'prediction': float(ensemble_pred),
                    'individual_predictions': {k: float(v) for k, v in predictions.items()},
                    'model_used': 'ensemble'
                }
            
            elif model_name in self.models:
                # Individual model prediction
                pred = self.models[model_name].predict(processed_features)[0]
                return {
                    'prediction': float(pred),
                    'model_used': model_name
                }
            
            else:
                raise ValueError(f"Model '{model_name}' not available. Available models: {list(self.models.keys()) + ['ensemble']}")
                
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise

# Initialize predictor (will be loaded when first accessed)
predictor = None

def get_predictor():
    """Get or initialize the predictor"""
    global predictor
    if predictor is None:
        # Get model directory (parent directory of this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels
        predictor = NQH2OPredictor(model_dir)
        predictor.load_models()
    return predictor

@prediction_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    try:
        pred = get_predictor()
        return jsonify({
            'status': 'healthy',
            'models_loaded': pred.is_loaded,
            'available_models': list(pred.models.keys()) + ['ensemble'],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@prediction_bp.route('/predict', methods=['POST'])
@cross_origin()
def predict():
    """Main prediction endpoint"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract features and model preference
        features = data.get('features', {})
        model_name = data.get('model', 'ensemble')
        
        if not features:
            return jsonify({'error': 'No features provided'}), 400
        
        # Get predictor and make prediction
        pred = get_predictor()
        result = pred.predict(features, model_name)
        
        # Add metadata
        result['timestamp'] = datetime.now().isoformat()
        result['features_used'] = len(features)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@prediction_bp.route('/models', methods=['GET'])
@cross_origin()
def list_models():
    """List available models and their information"""
    try:
        pred = get_predictor()
        
        model_info = {}
        for model_name in pred.models.keys():
            model_info[model_name] = {
                'type': type(pred.models[model_name]).__name__,
                'available': True
            }
        
        # Add ensemble info
        model_info['ensemble'] = {
            'type': 'WeightedEnsemble',
            'available': len(pred.ensemble_weights) > 0,
            'weights': pred.ensemble_weights
        }
        
        return jsonify({
            'models': model_info,
            'feature_count': len(pred.feature_names),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@prediction_bp.route('/features', methods=['GET'])
@cross_origin()
def list_features():
    """List required features for prediction"""
    try:
        pred = get_predictor()
        
        return jsonify({
            'features': pred.feature_names,
            'feature_count': len(pred.feature_names),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@prediction_bp.route('/example', methods=['GET'])
@cross_origin()
def prediction_example():
    """Provide an example prediction request"""
    try:
        pred = get_predictor()
        
        # Create example features (using zeros for simplicity)
        example_features = {feature: 0.0 for feature in pred.feature_names}
        
        # Add some realistic values for key features
        example_features.update({
            'nqh2o_lag_1': 400.0,  # Previous week's price
            'nqh2o_lag_2': 395.0,  # Two weeks ago
            'time_trend': 1000.0,  # Time trend
            'drought_composite_spi': -1.0,  # Moderate drought
            'is_drought_season': 1.0  # During drought season
        })
        
        example_request = {
            'features': example_features,
            'model': 'ensemble'
        }
        
        return jsonify({
            'example_request': example_request,
            'description': 'Example request body for /predict endpoint',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

