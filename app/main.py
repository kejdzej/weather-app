import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

params = {
    'q': 'Lublin',
    'appid': API_KEY,  
    'units': 'metric'  
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"Pogoda w {data['name']}: {data['weather'][0]['description']}")
    print(f"Temperatura: {data['main']['temp']}°C")
else:
    print(f"Błąd {response.status_code}: {response.json().get('message', 'Brak szczegółowych informacji')}")
