import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime
import aiohttp
import json

logger = logging.getLogger(__name__)

class AdvancedFeatureEngineering:
    def __init__(self):
        self.weather_api_key = None  # Set this in .env
        self.track_types = {
            'street_circuit': ['Monaco', 'Singapore', 'Baku', 'Miami'],
            'high_speed': ['Monza', 'Silverstone', 'Spa'],
            'technical': ['Hungaroring', 'Suzuka', 'Interlagos'],
            'power_circuit': ['Red Bull Ring', 'Paul Ricard']
        }

    async def fetch_weather_data(self, race_date, location):
        """Fetch historical weather data for a race"""
        try:
            # This is a placeholder - you'd need to implement actual weather API calls
            # Example using OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location,
                'appid': self.weather_api_key,
                'dt': int(datetime.strptime(race_date, '%Y-%m-%d').timestamp())
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'temperature': data['main']['temp'],
                            'humidity': data['main']['humidity'],
                            'wind_speed': data['wind']['speed'],
                            'conditions': data['weather'][0]['main']
                        }
                    return None
        except Exception as e:
            logger.error(f"Error fetching weather data: {str(e)}")
            return None

    def get_track_type(self, race_name):
        """Determine the type of track based on race name"""
        for track_type, tracks in self.track_types.items():
            if any(track in race_name for track in tracks):
                return track_type
        return 'unknown'

    def calculate_sector_performance(self, df):
        """Calculate sector time performance metrics"""
        try:
            # This is a placeholder - you'd need actual sector time data
            # For now, we'll create synthetic sector times
            df['sector1_time'] = np.random.normal(30, 2, len(df))
            df['sector2_time'] = np.random.normal(30, 2, len(df))
            df['sector3_time'] = np.random.normal(30, 2, len(df))
            
            # Calculate sector performance metrics
            for sector in [1, 2, 3]:
                df[f'sector{sector}_rank'] = df.groupby('race_name')[f'sector{sector}_time'].rank()
                df[f'sector{sector}_percentile'] = df[f'sector{sector}_rank'] / df.groupby('race_name')[f'sector{sector}_time'].transform('count')
            
            return df
        except Exception as e:
            logger.error(f"Error calculating sector performance: {str(e)}")
            return df

    def create_track_specific_features(self, df):
        """Create features based on track-specific performance"""
        try:
            # Add track type
            df['track_type'] = df['race_name'].apply(self.get_track_type)
            
            # Calculate track-specific performance
            track_performance = df.groupby(['driver_name', 'track_type'])['points'].mean().reset_index()
            
            # Pivot to create track-specific performance columns
            track_performance_pivot = track_performance.pivot(
                index='driver_name',
                columns='track_type',
                values='points'
            ).fillna(0)
            
            # Merge back to main dataframe
            df = df.merge(track_performance_pivot, on='driver_name', how='left')
            
            return df
        except Exception as e:
            logger.error(f"Error creating track-specific features: {str(e)}")
            return df

    def create_weather_features(self, df, weather_data):
        """Create features based on weather conditions"""
        try:
            if weather_data:
                # Add weather features
                df['temperature'] = weather_data['temperature']
                df['humidity'] = weather_data['humidity']
                df['wind_speed'] = weather_data['wind_speed']
                df['weather_conditions'] = weather_data['conditions']
                
                # Create weather impact features
                df['weather_impact'] = df.apply(
                    lambda x: self._calculate_weather_impact(x, weather_data),
                    axis=1
                )
            
            return df
        except Exception as e:
            logger.error(f"Error creating weather features: {str(e)}")
            return df

    def _calculate_weather_impact(self, row, weather_data):
        """Calculate weather impact based on historical performance in similar conditions"""
        # This is a placeholder - you'd need to implement actual weather impact calculation
        return np.random.random()

    def create_ensemble_features(self, df):
        """Create features for ensemble model"""
        try:
            # Calculate rolling statistics
            df['points_rolling_mean'] = df.groupby('driver_name')['points'].transform(
                lambda x: x.rolling(window=3, min_periods=1).mean()
            )
            df['points_rolling_std'] = df.groupby('driver_name')['points'].transform(
                lambda x: x.rolling(window=3, min_periods=1).std()
            )
            
            # Calculate position changes
            df['position_change'] = df['grid'] - df['position']
            
            # Calculate consistency metrics
            df['consistency_score'] = df.groupby('driver_name')['position'].transform(
                lambda x: 1 / (x.std() + 1)
            )
            
            return df
        except Exception as e:
            logger.error(f"Error creating ensemble features: {str(e)}")
            return df

    def prepare_features(self, df, weather_data=None):
        """Prepare all features for model training"""
        try:
            # Apply all feature engineering steps
            df = self.calculate_sector_performance(df)
            df = self.create_track_specific_features(df)
            df = self.create_weather_features(df, weather_data)
            df = self.create_ensemble_features(df)
            
            # Select final feature set
            feature_columns = [
                'recent_points', 'grid_position', 'constructor_strength',
                'driver_experience', 'sector1_percentile', 'sector2_percentile',
                'sector3_percentile', 'points_rolling_mean', 'points_rolling_std',
                'position_change', 'consistency_score', 'weather_impact'
            ]
            
            # Add track-specific performance columns
            feature_columns.extend([col for col in df.columns if col in self.track_types.keys()])
            
            # Handle missing values
            X = df[feature_columns].fillna(0)
            
            return X
        except Exception as e:
            logger.error(f"Error preparing features: {str(e)}")
            raise 