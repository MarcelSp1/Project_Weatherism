import pandas as pd
from collections import defaultdict
import os
import csv

# Datei laden
data = pd.read_csv('./csv_data/humidity_and_temperature.csv')

# Datum und Uhrzeit zusammenfassen in eine Zeile
data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'])
data['hour'] = data['datetime'].dt.hour
data['date'] = data['datetime'].dt.date

# LÖSCHEN
# Ergebnisstruktur vorbereiten 
result = defaultdict(lambda: defaultdict(lambda: {"humidity": [], "temperature": []}))

# Werte nach Datum und Stunde gruppieren und zusammenfassen
for _, row in data.iterrows():
    date = row['date']
    hour = row['hour']
    result[date][hour]['humidity'].append(row['humidity'])
    result[date][hour]['temperature'].append(row['temperature'])

def error_count():
    errors = []
    log_file = './evaluation/errors.log'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'w', encoding='utf-8') as log:
        for date, hours in result.items():
            for hour, values in hours.items():
                if len(values['humidity']) < 30:
                    error_message = f"Nicht genug Daten für {date} um {hour} Uhr. Nur {len(values['humidity'])} Daten gefunden.\n"
                    errors.append(error_message)
                    log.write(error_message)

data = []
hourly_data = './csv_data/hourly_data.csv'
with open(hourly_data, 'w', encoding='utf-8') as csv:
    for date, hours in result.items():
        for hour, values in hours.items():
            error_count()
            values['average_humidity'] = sum(values['humidity']) / len(values['humidity'])
            values['average_temperature'] = sum(values['temperature']) / len(values['temperature'])
            hourly= f"{date}, {hour}:00 {values['average_temperature']};{values['average_humidity']}\n"
            data.append(hourly)
            csv.write(hourly)

