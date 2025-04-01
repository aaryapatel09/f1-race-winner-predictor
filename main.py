import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.web.routes import router as web_router
from src.ml.ensemble_model import EnsembleF1Predictor
from src.data_collection.scraper import F1DataScraper
from src.automation.scheduler import F1Automation
from src.ml.feature_engineering import AdvancedFeatureEngineering
import asyncio
from datetime import datetime
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="F1 Race Predictor")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")

# Include web routes
app.include_router(web_router)

# Initialize components
predictor = EnsembleF1Predictor()
scraper = F1DataScraper()
feature_engineering = AdvancedFeatureEngineering()
automation = F1Automation()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if model is loaded
        model_loaded = await predictor.load_models()
        
        # Check if data exists
        data_exists = os.path.exists("data/latest_race_data.csv")
        
        return {
            "status": "healthy" if model_loaded and data_exists else "degraded",
            "model_loaded": model_loaded,
            "data_exists": data_exists,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    try:
        # Check if we need to update data
        if not os.path.exists("data/latest_race_data.csv"):
            logger.info("No data found. Starting data collection...")
            await scraper.collect_data()
            scraper.preprocess_data()
        
        # Load or train the model
        if not os.path.exists("models/f1_predictor.pkl"):
            logger.info("No model found. Training new model...")
            df = pd.read_csv("data/preprocessed_data.csv")
            X = feature_engineering.prepare_features(df)
            y = df['position'].values
            await predictor.train(X, y)
        else:
            await predictor.load_model()
        
        # Start automation scheduler in background
        asyncio.create_task(automation.run())
            
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 