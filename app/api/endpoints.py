from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime

from app.database import crud, session
from app.services.weather_service import weather_service
from app.schemas.weather import WeatherResponse
from app.core.config import settings
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# ========== API ENDPOINTS ==========

@router.get("/api/weather/current", response_model=WeatherResponse)
async def get_current_weather(
    city: str = Query(..., example="São Paulo"),
    country: Optional[str] = Query(None, example="BR"),
    db: Session = Depends(session.get_db)
):
    try:
        weather_data = weather_service.get_current_weather(city, country)
        db_record = crud.create_weather_record(db, weather_data)
        return db_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/weather/history", response_model=List[WeatherResponse])
async def get_weather_history(
    city: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(session.get_db)
):
    records = crud.get_weather_records(db, city=city, limit=limit)
    return records

@router.get("/api/weather/cities")
async def get_cities(db: Session = Depends(session.get_db)):
    return crud.get_cities_with_records(db)

# ========== FRONTEND ENDPOINTS ==========

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "app_name": settings.APP_NAME
    })

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    city: str = Query("São Paulo"),
    db: Session = Depends(session.get_db)
):
    try:
        current_data = weather_service.get_current_weather(city)
        crud.create_weather_record(db, current_data)
        
        history = crud.get_weather_records(db, city=city, limit=20)
        
        chart_data = {
            "dates": [r.timestamp.strftime("%H:%M") for r in history],
            "temperatures": [r.temperature for r in history],
            "humidities": [r.humidity for r in history]
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "app_name": settings.APP_NAME,
            "city": city,
            "current_data": current_data,
            "chart_data": json.dumps(chart_data),
            "has_real_data": current_data.get("source") == "openweathermap",
            "api_key_configured": bool(settings.OPENWEATHER_API_KEY and settings.OPENWEATHER_API_KEY != "test_key"),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        })
        
    except Exception as e:
        return f"<h1>Erro</h1><p>{str(e)}</p>"