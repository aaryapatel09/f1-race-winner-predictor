import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import logging
import os

logger = logging.getLogger(__name__)

class F1Predictor:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.model_path = "models/f1_predictor.pkl"
        self.scaler_path = "models/scaler.pkl"
        os.makedirs("models", exist_ok=True)

    async def train(self):
        """Train the prediction model"""
        try:
            # Load preprocessed data
            df = pd.read_csv("data/preprocessed_data.csv")
            
            # Prepare features
            X = self._prepare_features(df)
            y = df['position'].values
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.model.score(X_train_scaled, y_train)
            test_score = self.model.score(X_test_scaled, y_test)
            
            logger.info(f"Model trained successfully. Train score: {train_score:.3f}, Test score: {test_score:.3f}")
            
            # Save model and scaler
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise

    async def load_model(self):
        """Load the trained model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                logger.info("Model loaded successfully")
            else:
                logger.warning("No saved model found. Training new model...")
                await self.train()
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def _prepare_features(self, df):
        """Prepare features for model training"""
        # Create numerical features
        features = pd.DataFrame()
        
        # Driver form
        features['recent_points'] = df['recent_points'].fillna(0)
        
        # Grid position
        features['grid_position'] = pd.to_numeric(df['grid'], errors='coerce').fillna(20)
        
        # Constructor performance (average points per race)
        constructor_points = df.groupby('constructor')['points'].mean()
        features['constructor_strength'] = df['constructor'].map(constructor_points)
        
        # Driver experience (number of races)
        driver_experience = df.groupby('driver_name').size()
        features['driver_experience'] = df['driver_name'].map(driver_experience)
        
        return features

    async def predict_race(self, race_data):
        """Predict race outcome for given race data"""
        try:
            # Prepare features
            X = self._prepare_features(pd.DataFrame(race_data))
            X_scaled = self.scaler.transform(X)
            
            # Get predictions and probabilities
            predictions = self.model.predict(X_scaled)
            probabilities = self.model.predict_proba(X_scaled)
            
            # Get top 3 predictions with confidence scores
            results = []
            for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
                results.append({
                    'driver_name': race_data[i]['driver_name'],
                    'predicted_position': int(pred),
                    'confidence_score': float(max(prob))
                })
            
            # Sort by predicted position
            results.sort(key=lambda x: x['predicted_position'])
            
            return results[:3]
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise 