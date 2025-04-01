from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
import json

from src.ml.model import F1Predictor

router = APIRouter()
templates = Jinja2Templates(directory="src/web/templates")
predictor = F1Predictor()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "predictions": None}
    )

@router.post("/predict", response_class=HTMLResponse)
async def predict(
    request: Request,
    drivers: str = Form(...),
    constructors: str = Form(...),
    grid_positions: str = Form(...)
):
    """Handle race prediction request"""
    try:
        # Parse input data
        driver_list = json.loads(drivers)
        constructor_list = json.loads(constructors)
        grid_list = json.loads(grid_positions)
        
        # Prepare race data
        race_data = []
        for driver, constructor, grid in zip(driver_list, constructor_list, grid_list):
            race_data.append({
                'driver_name': driver,
                'constructor': constructor,
                'grid': grid
            })
        
        # Get predictions
        predictions = await predictor.predict_race(race_data)
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "predictions": predictions,
                "race_data": race_data
            }
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": str(e),
                "predictions": None
            }
        ) 