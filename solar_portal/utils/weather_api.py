"""
Weather API Client Module
Fetches external weather data for validation
"""

import requests
import pandas as pd
import logging
from datetime import datetime, timedelta
from config import API_CONFIG, LOCATION

logger = logging.getLogger(__name__)


class WeatherAPIClient:
    """
    Fetches weather data from Open-Meteo or NASA POWER APIs.
    Used for validation and comparison with sensor data.
    """
    
    def __init__(self, api: str = "open_meteo"):
        """
        Initialize weather API client.
        
        Args:
            api: "open_meteo" or "nasa_power"
        """
        self.api = api
        self.weather_data = None
        
    def fetch_open_meteo(self, 
                        latitude: float,
                        longitude: float,
                        start_date: str,
                        end_date: str) -> pd.DataFrame:
        """
        Fetch data from Open-Meteo API.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with weather data
        """
        url = API_CONFIG["open_meteo"]["url"]
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "hourly": ["shortwave_radiation", "cloud_cover"],
            "timezone": LOCATION.get("timezone", "UTC"),
        }
        
        try:
            response = requests.get(url, params=params, 
                                   timeout=API_CONFIG["open_meteo"]["timeout"])
            response.raise_for_status()
            
            data = response.json()
            
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(data["hourly"]["time"]),
                "poa_irradiance_Wm2": data["hourly"]["shortwave_radiation"],
                "cloud_cover_percent": data["hourly"]["cloud_cover"],
            })
            
            self.weather_data = df
            logger.info(f"Fetched {len(df)} weather records from Open-Meteo")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Open-Meteo data: {str(e)}")
            return pd.DataFrame()
    
    def fetch_weather(self,
                     latitude: float,
                     longitude: float,
                     start_date: str,
                     end_date: str) -> pd.DataFrame:
        """
        Fetch weather data using configured API.
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame with weather data
        """
        if self.api == "open_meteo":
            return self.fetch_open_meteo(latitude, longitude, start_date, end_date)
        else:
            logger.warning(f"API '{self.api}' not implemented, returning empty DataFrame")
            return pd.DataFrame()
    
    def get_weather_data(self) -> pd.DataFrame:
        """Get cached weather data"""
        if self.weather_data is None:
            return pd.DataFrame()
        return self.weather_data.copy()
