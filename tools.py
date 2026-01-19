import requests
import io
import pandas as pd

# --- PROFESSIONAL GRADE DATA HANDLER ---

def fetch_fire_data(nasa_key):
    """
    Fetches active fire data from NASA VIIRS.
    FALLBACK: If no key is provided, returns a high-fidelity simulation
    of a wildfire in the Angeles National Forest.
    """
    # 1. SIMULATION MODE (Safe, Deterministic for Demos)
    if not nasa_key or "YOUR_KEY" in nasa_key:
        return {
            "lat": 34.2437,       # Angeles National Forest
            "lon": -118.1522,
            "brightness": 450.5,  # Kelvin (Very Hot)
            "confidence": "high",
            "source": "SIMULATION_MODE"
        }

    # 2. REAL-WORLD MODE (Production Ready)
    # Coordinates for California Sensor Range
    coords = "-124.4,32.5,-114.1,42.0"
    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{nasa_key}/VIIRS_SNPP_NRT/{coords}/1"
    
    try:
        response = requests.get(url, timeout=10) # 10s timeout for safety
        if response.status_code != 200 or "No Data" in response.text:
            return None
        
        df = pd.read_csv(io.StringIO(response.text))
        high_conf = df[df['confidence'] != 'low']
        
        if high_conf.empty:
            return None
            
        # Select the most critical hotspot
        hottest = high_conf.loc[high_conf['bright_ti4'].idxmax()]
        return {
            "lat": hottest['latitude'],
            "lon": hottest['longitude'],
            "brightness": hottest['bright_ti4'],
            "source": "NASA_VIIRS_SATELLITE"
        }
    except Exception as e:
        print(f"[SYSTEM ERROR] API Connection Failed: {e}")
        return None

def fetch_weather_data(lat, lon):
    """
    Fetches real-time wind vectors from Open-Meteo.
    This API is free and does not require a key.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "wind_speed_10m,wind_direction_10m"
    }
    try:
        response = requests.get(url, params=params, timeout=5).json()
        current = response.get('current', {})
        return {
            "wind_speed_10m": current.get('wind_speed_10m', 0),
            "wind_direction_10m": current.get('wind_direction_10m', 0)
        }
    except Exception as e:
        return {"wind_speed_10m": 0, "wind_direction_10m": 0}