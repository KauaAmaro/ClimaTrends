import requests
from datetime import datetime
from typing import Optional, Dict, Any
from app.core.config import settings

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.api_key = settings.OPENWEATHER_API_KEY
    
    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key or self.api_key == "test_key":
            return self._get_mock_data(city, country_code)
        
        try:
            location = f"{city},{country_code}" if country_code else city
            
            response = requests.get(
                f"{self.base_url}/weather",
                params={
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",
                    "lang": "pt_br"
                },
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "city": data.get("name", ""),
                "country": data.get("sys", {}).get("country", ""),
                "temperature": data.get("main", {}).get("temp", 0),
                "feels_like": data.get("main", {}).get("feels_like", 0),
                "humidity": data.get("main", {}).get("humidity", 0),
                "pressure": data.get("main", {}).get("pressure", 0),
                "wind_speed": data.get("wind", {}).get("speed", 0),
                "description": data.get("weather", [{}])[0].get("description", ""),
                "weather_icon": data.get("weather", [{}])[0].get("icon", ""),
                "api_timestamp": datetime.fromtimestamp(data.get("dt", 0)),
                "source": "openweathermap"
            }
            
        except Exception as e:
            print(f"Erro: {e}")
            return self._get_mock_data(city, country_code)
    
    def _get_mock_data(self, city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        return {
            "city": city,
            "country": country_code or "BR",
            "temperature": 25.5,
            "feels_like": 27.0,
            "humidity": 65,
            "pressure": 1013,
            "wind_speed": 5.2,
            "description": "céu limpo",
            "weather_icon": "01d",
            "api_timestamp": datetime.utcnow(),
            "source": "mock_data"
        }

weather_service = WeatherService()