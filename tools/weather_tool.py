import os
import requests
from typing import Dict, Any

class WeatherTool:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city: str) -> Dict[str, Any]:
        if not city:
            return {"error": "City parameter is required"}
        
        if not self.api_key:
            return {"error": "OPENWEATHER_API_KEY not configured"}
        
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "city": data.get("name"),
                "country": data.get("sys", {}).get("country"),
                "temperature": f"{data['main'].get('temp')}°C",
                "feels_like": f"{data['main'].get('feels_like')}°C",
                "condition": data["weather"][0].get("description"),
                "humidity": f"{data['main'].get('humidity')}%",
                "wind_speed": f"{data.get('wind', {}).get('speed')} m/s",
                "pressure": f"{data['main'].get('pressure')} hPa"
            }
            
        except requests.exceptions.RequestException as e:
            return {"error": f"Weather API request failed: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}