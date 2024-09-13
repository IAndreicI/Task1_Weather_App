from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

key = "16615b5445834c7ca3c110005241209"
request_url = "http://api.weatherapi.com/v1/forecast.json"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class history(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(10))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    max_temp = db.Column(db.Float)
    min_temp = db.Column(db.Float)
    precipitation = db.Column(db.Float)
    sunrise = db.Column(db.String(10))
    sunset = db.Column(db.String(10))
    wind = db.Column(db.String(10))

    def __init__(self, date, city, country, max_temp, min_temp, precipitation, sunrise, sunset, wind):
        self.date = date
        self.city = city
        self.country = country
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.precipitation = precipitation
        self.sunrise = sunrise
        self.sunset = sunset
        self.wind = wind

def store_history(data_w):
    city = data_w["location"]["name"]
    country = data_w["location"]["country"]

    for day in data_w["forecast"]["forecastday"]:
        date = day["date"]
        max_temp = day["day"]["maxtemp_c"]
        min_temp = day["day"]["mintemp_c"]
        precipitation = day["day"]["totalprecip_mm"]
        sunrise = day["astro"]["sunrise"]
        sunset = day["astro"]["sunset"]
        wind = day["day"]["maxwind_kph"]

        found_history=history.query.filter_by(date=date, city=city).first()

        if found_history:
            found_history.max_temp=max_temp
            found_history.min_temp=min_temp
            found_history.precipitation=precipitation
            found_history.sunrise=sunrise
            found_history.sunset=sunset
            found_history.wind=wind
            db.session.commit()
        else:
            db.session.add(history(date,city,country,max_temp,min_temp,precipitation,sunrise,sunset,wind))
            db.session.commit()


@app.route("/", methods=["POST", "GET"])
def home():
    forecast_weather = None
    if request.method == "POST":
        city = request.form.get("city")
        forecast_weather = forecast(city)
        if forecast_weather != "Error" and forecast_weather != None:
            store_history(forecast_weather)

    return render_template("index.html", data_fw = forecast_weather)

def forecast(city):
    response = requests.get(request_url , params={
        "key": key,
        "q": city,
        "days": 3,
        "aqi": "no",
        "alerts":"no",
    })
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 400:
        return "Error"
    else:
        return None
    


@app.route("/database")
def database():
    return render_template("database.html", history = history.query.all())

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run()
