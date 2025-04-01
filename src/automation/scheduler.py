import schedule
import time
import asyncio
import logging
from datetime import datetime
import os
import json
import aiohttp
from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.data_collection.scraper import F1DataScraper
from src.ml.ensemble_model import EnsembleF1Predictor
from src.ml.feature_engineering import AdvancedFeatureEngineering

logger = logging.getLogger(__name__)

class F1Automation:
    def __init__(self):
        self.scraper = F1DataScraper()
        self.predictor = EnsembleF1Predictor()
        self.feature_engineering = AdvancedFeatureEngineering()
        self.notification_email = os.getenv('NOTIFICATION_EMAIL')
        self.smtp_server = os.getenv('SMTP_SERVER')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

    async def update_data_and_model(self):
        """Update race data and retrain model"""
        try:
            logger.info("Starting data update and model retraining...")
            
            # Collect new data
            await self.scraper.collect_data()
            
            # Preprocess data
            df = pd.read_csv("data/latest_race_data.csv")
            df = self.scraper.preprocess_data()
            
            # Get weather data for next race
            next_race = self._get_next_race_info()
            weather_data = await self.feature_engineering.fetch_weather_data(
                next_race['date'],
                next_race['location']
            )
            
            # Prepare features
            X = self.feature_engineering.prepare_features(df, weather_data)
            y = df['position'].values
            
            # Train model
            model_scores = await self.predictor.train(X, y)
            
            # Generate report
            report = self._generate_update_report(model_scores)
            
            # Send notification
            await self._send_notification(report)
            
            logger.info("Data update and model retraining completed successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error in update_data_and_model: {str(e)}")
            await self._send_error_notification(str(e))
            raise

    def _get_next_race_info(self) -> Dict[str, Any]:
        """Get information about the next race"""
        # This is a placeholder - you'd need to implement actual race schedule lookup
        return {
            'date': '2024-03-24',
            'location': 'Melbourne, Australia',
            'track': 'Albert Park Circuit'
        }

    def _generate_update_report(self, model_scores: Dict[str, float]) -> str:
        """Generate a report about the update"""
        report = f"""
F1 Prediction Model Update Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Model Performance:
{'-' * 20}
"""
        for model_name, score in model_scores.items():
            report += f"{model_name}: {score:.3f}\n"
        
        report += f"""
Ensemble Weights:
{'-' * 20}
"""
        for model_name, weight in self.predictor.weights.items():
            report += f"{model_name}: {weight:.2f}\n"
        
        return report

    async def _send_notification(self, report: str):
        """Send email notification about the update"""
        if not all([self.notification_email, self.smtp_server, self.smtp_username, self.smtp_password]):
            logger.warning("Email notification settings not configured")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.notification_email
            msg['Subject'] = "F1 Prediction Model Update Complete"
            
            msg.attach(MIMEText(report, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info("Notification email sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending notification email: {str(e)}")

    async def _send_error_notification(self, error_message: str):
        """Send email notification about errors"""
        if not all([self.notification_email, self.smtp_server, self.smtp_username, self.smtp_password]):
            logger.warning("Email notification settings not configured")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.notification_email
            msg['Subject'] = "F1 Prediction Model Update Failed"
            
            body = f"""
Error occurred during model update:
{error_message}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info("Error notification email sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending error notification email: {str(e)}")

    def schedule_updates(self):
        """Schedule regular updates"""
        # Schedule weekly data updates
        schedule.every().week.at("00:00").do(
            lambda: asyncio.run(self.update_data_and_model())
        )
        
        # Schedule daily model performance checks
        schedule.every().day.at("12:00").do(
            lambda: asyncio.run(self._check_model_performance())
        )
        
        logger.info("Update schedule configured")

    async def _check_model_performance(self):
        """Check model performance and trigger retraining if needed"""
        try:
            # Load current model scores
            if os.path.exists("models/model_scores.json"):
                with open("models/model_scores.json", 'r') as f:
                    current_scores = json.load(f)
                
                # Check if any model's performance has degraded
                for model_name, score in current_scores.items():
                    if score < 0.5:  # Performance threshold
                        logger.warning(f"Model {model_name} performance degraded. Triggering retraining...")
                        await self.update_data_and_model()
                        break
                        
        except Exception as e:
            logger.error(f"Error checking model performance: {str(e)}")

    def run(self):
        """Run the automation scheduler"""
        self.schedule_updates()
        logger.info("Starting automation scheduler...")
        
        while True:
            schedule.run_pending()
            time.sleep(60) 