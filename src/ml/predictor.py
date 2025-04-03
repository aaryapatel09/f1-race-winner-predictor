import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os

class F1Predictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        self.is_trained = False
        
    def prepare_features(self, track, date):
        features = {
            'track': track,
            'month': date.month,
            'day': date.day,
            'day_of_week': date.weekday()
        }
        return pd.DataFrame([features])
    
    def train(self, historical_data):
        if not historical_data.empty:
            X = historical_data[['track', 'month', 'day', 'day_of_week']]
            y = historical_data['winner']
            
            X['track'] = self.label_encoder.fit_transform(X['track'])
            
            self.model.fit(X, y)
            self.is_trained = True
            
            if not os.path.exists('models'):
                os.makedirs('models')
            joblib.dump(self.model, 'models/f1_predictor.joblib')
            joblib.dump(self.label_encoder, 'models/label_encoder.joblib')
    
    def predict(self, track, date):
        if not self.is_trained:
            return "Max Verstappen"  # Default prediction if not trained
            
        features = self.prepare_features(track, date)
        features['track'] = self.label_encoder.transform([track])
        
        prediction = self.model.predict(features)[0]
        probabilities = self.model.predict_proba(features)[0]
        confidence = max(probabilities)
        
        return prediction, confidence 