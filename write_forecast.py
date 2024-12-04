import openmeteo_requests
import requests
import pandas as pd
from retry_requests import retry

# Erstelle den Open Meteo API-Client mit erneutem Versuch, falls Open Meteo nicht die benötigte Antwort sendet
retry_session = retry(requests.Session(), retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Definiere die API, von der die Daten abgerufen werden
url = "https://api.open-meteo.com/v1/forecast"

# Definiere, für welchen Ort und welche Daten abgerufen werden
params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"hourly": ["temperature_2m", "relative_humidity_2m", "rain"],
	"forecast_days": 2
}
# Frage die in params festgelegten Parameter ab und speichere die Antwort in der Variable responses
# (Die Variable responses stellt nur einen Verweis auf den Speicherort der empfangenen Antwort dar.
# Für besseres Verständnis kann das nachfolgende print() statement auskommentiert werden.)
responses = openmeteo.weather_api(url, params=params)
# print(responses)

# Picke gezielt die Antwort mit den angeforderten Variablen aus ihrem Speicherort herraus und speichere diese in response
response = responses[0]

# Im Folgenden werden die stündlichen Daten verarbeitet. Die Reihenfolge der Variablen muss die gleiche sein, wie sie in params definiert wurden.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_rain = hourly.Variables(2).ValuesAsNumpy()

##
#
#
#
##
hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

#
hourly_data["Temperatur"] = hourly_temperature_2m
hourly_data["Luftfeuchtigkeit"] = hourly_relative_humidity_2m
hourly_data["Regen"] = hourly_rain

# Spalte mit Datum der Erzeugung hinten anhängen
generated_at = pd.Timestamp.now()
hourly_data["generated_at"] = [generated_at] * len(hourly_data["date"])

# Erstelle aus hourly_data einen lesbaren Dataframe mit dem Namen hourly_dataframe
hourly_dataframe = pd.DataFrame(data = hourly_data)

# Die Spalte mit dem Datum der Erzeugung an die erste Stelle schieben
# Dabei wird die letzte Spalte, also [generated_at] an die erste Position gestellt und
# Die restlichen Spalten dahintergehangen, solange sie nicht [generated_at] sind
cols = ["generated_at"] + [col for col in hourly_dataframe.columns if col != "generated_at"]
hourly_dataframe = hourly_dataframe[cols]

# Schreibe den Zuvor erstellten und richtig sortierten Dataframe zur Abspeicherung in csv_data/wetter.csv
csv_file = 'csv_data/wetter.csv'
hourly_dataframe.to_csv(csv_file, mode='a', header=False, index=False)
