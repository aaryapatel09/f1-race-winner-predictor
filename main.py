import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from src.web.routes import router as web_router
from src.ml.model import F1Predictor
from src.data_collection.scraper import F1DataScraper

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
predictor = F1Predictor()
scraper = F1DataScraper()

@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    try:
        # Check if we need to update data
        if not os.path.exists("data/latest_race_data.csv"):
            logger.info("No data found. Starting data collection...")
            await scraper.collect_data()
        
        # Load or train the model
        if not os.path.exists("models/f1_predictor.pkl"):
            logger.info("No model found. Training new model...")
            await predictor.train()
        else:
            await predictor.load_model()
            
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 