import pandas as pd
from collections import defaultdict
import os
import csv

print("Vorgang wird gestartet.")

# Datei laden
data = pd.read_csv('raw_data/modified_humidity_and_temperature.csv')

# Datum und Uhrzeit zusammenfassen in eine Zeile
data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'])
data['hour'] = data['datetime'].dt.hour
data['date'] = data['datetime'].dt.date

# Ergebnisstruktur vorbereiten 
result = defaultdict(lambda: defaultdict(lambda: {"humidity": [], "temperature": []}))

# Werte nach Datum und Stunde gruppieren und zusammenfassen
for _, row in data.iterrows():
    date = row['date']
    hour = row['hour']
    result[date][hour]['humidity'].append(row['humidity'])
    result[date][hour]['temperature'].append(row['temperature'])

def error_count():
    log_file = 'results/errors.log'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'w', encoding='utf-8') as log:
        for date, hours in result.items():
            for hour, values in hours.items():
                if len(values['humidity']) < 30:
                    error_message = f"Nicht genug Daten für {date} um {hour} Uhr. Nur {len(values['humidity'])} Daten gefunden.\n"
                    log.write(error_message)

data = []
hourly_data = 'results/hourly_data.csv'
with open(hourly_data, 'w', encoding='utf-8') as csv:
    for date, hours in result.items():
        for hour, values in hours.items():
            error_count()
            values['average_humidity'] = sum(values['humidity']) / len(values['humidity'])
            values['average_temperature'] = sum(values['temperature']) / len(values['temperature'])
            hourly= f"{date}, {hour}:00 {values['average_temperature']};{values['average_humidity']}\n"
            csv.write(hourly)

print("Vorgang wurde erfolgreich abgeschlossen.")
