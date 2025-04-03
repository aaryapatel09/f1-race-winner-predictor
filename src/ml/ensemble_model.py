import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_networks import MLPClassifier
import xgboost as xgb
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import logging
import os
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class EnsembleF1Predictor:
    def __init__(self):
        self.models = {
            'rf': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
            'gb': GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42),
            'xgb': xgb.XGBClassifier(n_estimators=100, max_depth=5, random_state=42),
            'lgb': lgb.LGBMClassifier(n_estimators=100, max_depth=5, random_state=42),
            'nn': MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        }
        self.scaler = StandardScaler()
        self.model_dir = "models"
        self.weights = {
            'rf': 0.3,
            'gb': 0.2,
            'xgb': 0.2,
            'lgb': 0.15,
            'nn': 0.15
        }
        os.makedirs(self.model_dir, exist_ok=True)

    async def train(self, X, y):
        """Train all models in the ensemble"""
        try:
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train each model
            model_scores = {}
            for name, model in self.models.items():
                logger.info(f"Training {name} model...")
                model.fit(X_train_scaled, y_train)
                score = model.score(X_test_scaled, y_test)
                model_scores[name] = score
                logger.info(f"{name} model score: {score:.3f}")
                
                # Save individual model
                joblib.dump(model, f"{self.model_dir}/{name}_model.pkl")
            
            # Save scaler
            joblib.dump(self.scaler, f"{self.model_dir}/scaler.pkl")
            
            # Save model scores for weight adjustment
            with open(f"{self.model_dir}/model_scores.json", 'w') as f:
                json.dump(model_scores, f)
            
            # Adjust weights based on performance
            self._adjust_weights(model_scores)
            
            return model_scores
            
        except Exception as e:
            logger.error(f"Error training ensemble: {str(e)}")
            raise

    def _adjust_weights(self, model_scores):
        """Adjust model weights based on their performance"""
        total_score = sum(model_scores.values())
        if total_score > 0:
            self.weights = {
                name: score / total_score
                for name, score in model_scores.items()
            }
            logger.info(f"Adjusted model weights: {self.weights}")

    async def load_models(self):
        """Load all trained models"""
        try:
            for name in self.models.keys():
                model_path = f"{self.model_dir}/{name}_model.pkl"
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)
                    logger.info(f"Loaded {name} model")
            
            if os.path.exists(f"{self.model_dir}/scaler.pkl"):
                self.scaler = joblib.load(f"{self.model_dir}/scaler.pkl")
                logger.info("Loaded scaler")
            
            if os.path.exists(f"{self.model_dir}/model_scores.json"):
                with open(f"{self.model_dir}/model_scores.json", 'r') as f:
                    model_scores = json.load(f)
                    self._adjust_weights(model_scores)
            
            return True
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            return False

    async def predict_race(self, X):
        """Make predictions using the ensemble"""
        try:
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Get predictions from each model
            all_predictions = {}
            all_probabilities = {}
            
            for name, model in self.models.items():
                pred = model.predict(X_scaled)
                prob = model.predict_proba(X_scaled)
                all_predictions[name] = pred
                all_probabilities[name] = prob
            
            # Combine predictions using weighted voting
            final_predictions = np.zeros(len(X))
            final_probabilities = np.zeros((len(X), len(np.unique(y))))
            
            for name in self.models.keys():
                final_predictions += all_predictions[name] * self.weights[name]
                final_probabilities += all_probabilities[name] * self.weights[name]
            
            # Round final predictions
            final_predictions = np.round(final_predictions).astype(int)
            
            return final_predictions, final_probabilities
            
        except Exception as e:
            logger.error(f"Error making ensemble predictions: {str(e)}")
            raise

    def generate_prediction_explanation(self, driver_name, prediction, probabilities, race_data):
        """Generate human-readable explanation of the prediction"""
        try:
            # Get top contributing factors
            feature_importance = self._get_feature_importance(race_data)
            
            # Generate explanation
            explanation = f"Based on our analysis, {driver_name} has a {probabilities.max()*100:.1f}% chance of finishing in position {prediction}. "
            
            # Add contributing factors
            top_factors = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:3]
            explanation += "This prediction is primarily based on: "
            explanation += ", ".join([f"{factor} ({importance:.1f}% impact)" for factor, importance in top_factors])
            
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating prediction explanation: {str(e)}")
            return "Unable to generate detailed explanation."

    def _get_feature_importance(self, race_data):
        """Calculate feature importance for explanation generation"""
        # This is a placeholder - you'd need to implement actual feature importance calculation
        return {
            'Recent Form': 0.3,
            'Track Performance': 0.25,
            'Weather Conditions': 0.2,
            'Grid Position': 0.15,
            'Team Performance': 0.1
        } 