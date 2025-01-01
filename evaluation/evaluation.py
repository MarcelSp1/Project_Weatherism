import pandas as pd
from collections import defaultdict
import os

# Datei laden
data = pd.read_csv('./csv_data/humidity_and_temperature.csv')

# Sicherstellen, dass die Zeitangaben richtig formatiert sind
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

# Prüfen, ob genügend Daten vorhanden sind und Fehler ausgeben, falls nicht
errors = []
log_file = './evaluation/errors.log'
os.makedirs(os.path.dirname(log_file), exist_ok=True)
with open(log_file, 'a', encoding='utf-8') as log:
    for date, hours in result.items():
        for hour, values in hours.items():
            if len(values['humidity']) < 30:
                error_message = f"Nicht genug Daten für {date} um {hour} Uhr. Nur {len(values['humidity'])} Daten gefunden.\n"
                errors.append(error_message)
                log.write(error_message)
    


# # Ergebnis anzeigen (als Beispiel für ein Datum)
example_date = next(iter(result))
example_output = {example_date: result[example_date]}
print("Example output:", example_output)

# # Speichern in einer Datei für weitere Verwendung
import json
output_file = './evaluation/grouped_data.json'
with open(output_file, 'w') as f:
    json.dump({str(date): {hour: dict(data) for hour, data in hours.items()} for date, hours in result.items()}, f)

print(f"Grouped data saved to {output_file}")

