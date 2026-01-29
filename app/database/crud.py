from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import WeatherRecord
from app.schemas.weather import WeatherCreate
from typing import List, Optional

def create_weather_record(db: Session, weather_data: dict):
    db_record = WeatherRecord(
        city=weather_data.get("city"),
        country=weather_data.get("country"),
        temperature=weather_data.get("temperature"),
        feels_like=weather_data.get("feels_like"),
        humidity=weather_data.get("humidity"),
        pressure=weather_data.get("pressure"),
        wind_speed=weather_data.get("wind_speed"),
        description=weather_data.get("description"),
        weather_icon=weather_data.get("weather_icon")
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_weather_records(
    db: Session, 
    city: Optional[str] = None, 
    limit: int = 100
) -> List[WeatherRecord]:
    query = db.query(WeatherRecord)
    if city:
        query = query.filter(WeatherRecord.city.ilike(f"%{city}%"))
    return query.order_by(desc(WeatherRecord.timestamp)).limit(limit).all()

def get_cities_with_records(db: Session) -> List[str]:
    records = db.query(WeatherRecord.city).distinct().all()
    return [record[0] for record in records]