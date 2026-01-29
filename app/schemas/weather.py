from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class WeatherBase(BaseModel):
    city: str = Field(..., example="São Paulo")
    country: str = Field(..., example="BR")
    temperature: float = Field(..., example=25.5)
    feels_like: float = Field(..., example=27.0)
    humidity: float = Field(..., example=65.0)
    pressure: float = Field(..., example=1013.0)
    wind_speed: float = Field(..., example=5.2)
    description: str = Field(..., example="céu limpo")
    weather_icon: str = Field(..., example="01d")

class WeatherCreate(WeatherBase):
    pass

class WeatherResponse(WeatherBase):
    id: int
    timestamp: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True