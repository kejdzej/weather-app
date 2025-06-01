# Zadanie 1 – Aplikacja pogodowa w kontenerze Docker

## Autor
Hubert Kwiatkowski

## Struktura katalogu
```
zadanie1/
├── app/
│   ├── main.py
│   ├── requirements.txt
├── Dockerfile
└── zadanie1.md
```

## Opis
Aplikacja webowa (Flask), która pozwala wybrać kraj i miasto i pokazuje aktualną pogodę korzystając z API OpenWeatherMap. Dane są logowane, a obraz kontenera jest zoptymalizowany.

## Kod

### `app/main.py`
```python
from flask import Flask, request, render_template_string
import datetime
import logging
import os
import requests

app = Flask(__name__)
PORT = int(os.environ.get("PORT", 4444))
AUTHOR = "Hubert Kwiatkowski"

logging.basicConfig(level=logging.INFO)
start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logging.info(f"Start: {start_time}, Autor: {AUTHOR}, Port: {PORT}")

API_KEY = "demo"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

COUNTRIES = {
    "PL": ["Warszawa", "Lublin", "Gdańsk"],
    "US": ["New York", "Los Angeles", "Chicago"],
    "FR": ["Paris", "Lyon", "Nice"]
}

@app.route("/", methods=["GET", "POST"])
def index():
    weather_info = ""
    selected_country = "PL"
    selected_city = "Warszawa"

    if request.method == "POST":
        selected_country = request.form.get("country")
        selected_city = request.form.get("city")
        params = {
            "q": selected_city,
            "appid": API_KEY,
            "units": "metric"
        }
        try:
            r = requests.get(WEATHER_URL, params=params)
            data = r.json()
            if r.status_code == 200:
                weather_info = f"Pogoda w {selected_city}: {data['weather'][0]['description']}, Temp: {data['main']['temp']}°C"
            else:
                weather_info = "Błąd podczas pobierania danych pogodowych"
        except Exception as e:
            weather_info = f"Błąd: {str(e)}"

    return render_template_string("""
        <h2>Wybierz kraj i miasto</h2>
        <form method="post">
            <label for="country">Kraj:</label>
            <select name="country" id="country" onchange="this.form.submit()">
                {% for c in countries %}
                <option value="{{c}}" {% if c == selected_country %}selected{% endif %}>{{c}}</option>
                {% endfor %}
            </select><br><br>

            <label for="city">Miasto:</label>
            <select name="city" id="city">
                {% for city in countries[selected_country] %}
                <option value="{{city}}" {% if city == selected_city %}selected{% endif %}>{{city}}</option>
                {% endfor %}
            </select><br><br>

            <input type="submit" value="Pokaż pogodę">
        </form>
        <p>{{weather_info}}</p>
    """, countries=COUNTRIES, selected_country=selected_country,
           selected_city=selected_city, weather_info=weather_info)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

```

### `app/requirements.txt`
```
flask
requests
```

### `Dockerfile`
```Dockerfile
FROM python:3.12-slim AS builder
LABEL org.opencontainers.image.authors="Hubert Kwiatkowski"
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY app/ /app/
EXPOSE 4444
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:4444 || exit 1
ENTRYPOINT ["python", "main.py"]
```

## Budowanie i uruchamianie kontenera

```bash
docker build -t pogoda-app .
docker run -d -p 4444:4444 --name pogoda pogoda-app
docker logs pogoda
docker image inspect pogoda-app --format '{{.RootFS.Layers}}'
docker image ls pogoda-app
```
.