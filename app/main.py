from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import uvicorn
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import random
import json

# Carregar variáveis de ambiente
load_dotenv()

print("API KEY carregada:", os.getenv("OPENWEATHER_API_KEY"))


app = FastAPI(title="ClimaTrends")

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Configurações da API OpenWeather
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "").strip()
OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather_data(city: str):
    """Busca dados de clima """
    
    print(f"\n Buscando clima para: {city}")
    
    # PRIMEIRO: Tenta OpenWeather se tiver chave válida
    if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "sua_chave_aqui":
        result = try_openweather(city)
        if result and not result.get("error"):
            return result
    
    # SEGUNDO: Tenta Open-Meteo (não precisa de chave)
    result = try_openmeteo(city)
    if result and not result.get("error"):
        return result
    
    # TERCEIRO: Retorna mock data
    print(f"  Todas as APIs falharam, usando dados mock")
    return get_mock_data(city, "APIs indisponíveis")

def try_openweather(city: str):
    """Tenta OpenWeather API"""
    try:
        params = {
            "q": city.replace(" ", "%20"),
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "lang": "pt_br"
        }
        
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params=params,
            timeout=8
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   OpenWeather: {data['main']['temp']}°C")
            return parse_openweather_data(data, city)
        else:
            print(f"  OpenWeather erro {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   OpenWeather falhou: {e}")
        return None

def try_openmeteo(city: str):
    """Usa Open-Meteo API (gratuita, sem chave)"""
    try:
        # Primeiro busca coordenadas da cidade
        geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        geo_params = {
            "name": city,
            "count": 1,
            "language": "pt",
            "format": "json"
        }
        
        geo_response = requests.get(geo_url, params=geo_params, timeout=8)
        
        if geo_response.status_code == 200:
            geo_data = geo_response.json()
            if geo_data.get("results"):
                location = geo_data["results"][0]
                
                # Agora busca dados climáticos
                weather_url = "https://api.open-meteo.com/v1/forecast"
                weather_params = {
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": "temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,weather_code",
                    "timezone": "auto"
                }
                
                weather_response = requests.get(weather_url, params=weather_params, timeout=8)
                
                if weather_response.status_code == 200:
                    weather_data = weather_response.json()["current"]
                    print(f"   Open-Meteo: {weather_data['temperature_2m']}°C")
                    
                    # Mapear weather_code para descrição
                    weather_codes = {
                        0: "Céu limpo", 1: "Poucas nuvens", 2: "Parcialmente nublado",
                        3: "Nublado", 45: "Nevoeiro", 48: "Nevoeiro com geada",
                        51: "Chuvisco leve", 53: "Chuvisco moderado", 55: "Chuvisco forte",
                        61: "Chuva leve", 63: "Chuva moderada", 65: "Chuva forte",
                        71: "Neve leve", 73: "Neve moderada", 75: "Neve forte",
                        80: "Pancadas de chuva leves", 81: "Pancadas de chuva fortes",
                        95: "Tempestade", 96: "Tempestade com granizo leve",
                        99: "Tempestade com granizo forte"
                    }
                    
                    desc = weather_codes.get(weather_data.get("weather_code", 0), "Desconhecido")
                    
                    return {
                        "city": location["name"],
                        "country": location.get("country_code", ""),
                        "temperature": weather_data["temperature_2m"],
                        "feels_like": weather_data["temperature_2m"],
                        "humidity": weather_data["relative_humidity_2m"],
                        "pressure": weather_data["pressure_msl"],
                        "description": desc,
                        "wind_speed": weather_data["wind_speed_10m"],
                        "icon": get_icon_from_code(weather_data.get("weather_code", 0)),
                        "timestamp": datetime.now().strftime("%H:%M"),
                        "error": False,
                        "source": "openmeteo"
                    }
                    
    except Exception as e:
        print(f"  Open-Meteo falhou: {e}")
    
    return None

def get_icon_from_code(code: int) -> str:
    """Converte código de clima para ícone"""
    icon_map = {
        0: "01d", 1: "02d", 2: "03d", 3: "04d",
        45: "50d", 48: "50d",
        51: "09d", 53: "09d", 55: "09d",
        61: "10d", 63: "10d", 65: "10d",
        71: "13d", 73: "13d", 75: "13d",
        80: "09d", 81: "09d",
        95: "11d", 96: "11d", 99: "11d"
    }
    return icon_map.get(code, "01d")

def parse_openweather_data(data, city):
    """Parse dados OpenWeather"""
    return {
        "city": data.get("name", city),
        "country": data.get("sys", {}).get("country", ""),
        "temperature": data.get("main", {}).get("temp", 0),
        "feels_like": data.get("main", {}).get("feels_like", 0),
        "humidity": data.get("main", {}).get("humidity", 0),
        "pressure": data.get("main", {}).get("pressure", 0),
        "description": data.get("weather", [{}])[0].get("description", "").capitalize(),
        "wind_speed": data.get("wind", {}).get("speed", 0),
        "icon": data.get("weather", [{}])[0].get("icon", "01d"),
        "timestamp": datetime.now().strftime("%H:%M"),
        "error": False,
        "source": "openweathermap"
    }

def get_mock_data(city: str, reason: str = "APIs indisponíveis"):
    """Retorna dados fixos quando as APIs não respondem"""
    return {
        "city": city,
        "country": "XX",
        "temperature": None,
        "feels_like": None,
        "humidity": None,
        "pressure": None,
        "description": "Dados indisponíveis",
        "wind_speed": None,
        "icon": "01d",
        "timestamp": datetime.now().strftime("%H:%M"),
        "error": True,
        "error_message": reason,
        "source": "fallback"
    }


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "app_name": "ClimaTrends",
            "api_key_configured": bool(OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "sua_chave_aqui")
        }
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, city: str = "São Paulo"):
    # Buscar dados (reais ou mock)
    weather_data = get_weather_data(city)
    
    # Verificar se são dados reais ou mock
    has_error = weather_data.get("error", True)  # Default para True por segurança
    is_real_data = weather_data.get("source") == "openweathermap"
    
    # Gerar dados para gráfico
    current_hour = datetime.now().hour
    times = []
    temperatures = []
    humidities = []
    
    # Simula últimas 6 horas
    for i in range(6, 0, -1):
        hour = (current_hour - i) % 24
        times.append(f"{hour:02d}:00")
        
        if is_real_data:
            # Variação baseada no valor real
            base_temp = weather_data["temperature"]
            base_hum = weather_data["humidity"]
            temp_variation = random.uniform(-3, 3)
            hum_variation = random.randint(-10, 10)
        else:
            # Variação aleatória para mock
            base_temp = random.uniform(10, 30)
            base_hum = random.randint(40, 90)
            temp_variation = random.uniform(-5, 5)
            hum_variation = random.randint(-15, 15)
        
        temperatures.append(round(base_temp + temp_variation, 1))
        humidities.append(max(20, min(100, base_hum + hum_variation)))
    
    chart_data = {
        "times": times,
        "temperatures": temperatures,
        "humidities": humidities
    }
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "app_name": "ClimaTrends",
            "city": city,
            "weather_data": weather_data,
            "chart_data": chart_data,
            "has_error": has_error,  
            "api_key_configured": bool(OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "sua_chave_aqui")
        }
    )

@app.get("/api/weather")
async def api_weather(city: str = "London"):
    """Endpoint API para dados JSON"""
    data = get_weather_data(city)
    return data

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "openweather_configured": bool(OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != "sua_chave_aqui"),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("=" * 50)
    print(" ClimaTrends API Iniciando...")
    print("=" * 50)
    print(f" API Key: {'Configurada' if OPENWEATHER_API_KEY and OPENWEATHER_API_KEY != 'sua_chave_aqui' else 'NÃO configurada'}")
    print(f"URL: http://localhost:8000")
    print(f" Dashboard: http://localhost:8000/dashboard")
    print(f" Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)