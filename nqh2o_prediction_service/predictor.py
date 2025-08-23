#!/usr/bin/env python3
"""
Vertex AI Custom Predictor for NQH2O Forecasting
Implements the required interface for Vertex AI custom containers
"""

import os
import json
import logging
import numpy as np
import pandas as pd
import joblib
from flask import Flask, request, jsonify
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NQH2OVertexPredictor:
    """
    Vertex AI compatible predictor for NQH2O forecasting
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = None
        self.feature_selector = None
        self.ensemble_weights = {}
        self.feature_names = []
        self.is_loaded = False
        
    def load_artifacts(self):
        """Load model artifacts"""
        try:
            logger.info("Loading model artifacts...")
            
            # Load models
            model_files = {
                'ridge': 'nqh2o_model_ridge.joblib',
                'lasso': 'nqh2o_model_lasso.joblib',
                'elastic_net': 'nqh2o_model_elastic_net.joblib',
                'random_forest': 'nqh2o_model_random_forest.joblib',
                'gradient_boosting': 'nqh2o_model_gradient_boosting.joblib'
            }
            
            for model_name, filename in model_files.items():
                if os.path.exists(filename):
                    self.models[model_name] = joblib.load(filename)
                    logger.info(f"✓ Loaded {model_name}")
            
            # Load preprocessing objects
            if os.path.exists('nqh2o_scalers.joblib'):
                self.scalers = joblib.load('nqh2o_scalers.joblib')
                logger.info("✓ Loaded scalers")
            
            if os.path.exists('nqh2o_feature_selector.joblib'):
                self.feature_selector = joblib.load('nqh2o_feature_selector.joblib')
                logger.info("✓ Loaded feature selector")
            
            if os.path.exists('nqh2o_ensemble_weights.joblib'):
                self.ensemble_weights = joblib.load('nqh2o_ensemble_weights.joblib')
                logger.info("✓ Loaded ensemble weights")
            
            # Load feature names
            if os.path.exists('nqh2o_feature_names.txt'):
                with open('nqh2o_feature_names.txt', 'r') as f:
                    self.feature_names = [line.strip() for line in f.readlines()]
                logger.info(f"✓ Loaded {len(self.feature_names)} feature names")
            
            self.is_loaded = True
            logger.info("✓ All artifacts loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading artifacts: {str(e)}")
            raise
    
    def preprocess(self, instances):
        """Preprocess input instances"""
        try:
            # Convert to DataFrame
            if isinstance(instances, list):
                df = pd.DataFrame(instances)
            else:
                df = pd.DataFrame([instances])
            
            # Ensure all features are present
            for feature in self.feature_names:
                if feature not in df.columns:
                    df[feature] = 0.0
            
            # Select features in correct order
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
            logger.error(f"Preprocessing error: {str(e)}")
            raise
    
    def predict(self, instances):
        """Make predictions"""
        try:
            # Preprocess
            processed_features = self.preprocess(instances)
            
            # Get predictions from all models
            predictions = {}
            for model_name, model in self.models.items():
                pred = model.predict(processed_features)
                predictions[model_name] = pred.tolist()
            
            # Calculate ensemble prediction
            ensemble_pred = np.zeros(len(processed_features))
            total_weight = 0.0
            
            for model_name, pred in predictions.items():
                weight = self.ensemble_weights.get(model_name, 1.0 / len(predictions))
                ensemble_pred += weight * np.array(pred)
                total_weight += weight
            
            if total_weight > 0:
                ensemble_pred /= total_weight
            
            return {
                'predictions': ensemble_pred.tolist(),
                'individual_predictions': predictions,
                'model_version': '1.0',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise

# Initialize predictor
predictor = NQH2OVertexPredictor()

# Flask app for Vertex AI
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor.is_loaded,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict', methods=['POST'])
def predict():
    """Prediction endpoint for Vertex AI"""
    try:
        # Get request data
        data = request.get_json()
        
        if 'instances' not in data:
            return jsonify({'error': 'Missing instances in request'}), 400
        
        # Make prediction
        result = predictor.predict(data['instances'])
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load model artifacts on startup
    predictor.load_artifacts()
    
    # Start Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
