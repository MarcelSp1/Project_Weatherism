import pandas as pd
from collections import defaultdict

# Werte pro Stunde zählen.
# Falls keine 30 vorhanden sind, wird dies in evaluation/results/errors.log vermerkt.
def error_count(result):
    log_file = 'evaluation/results/errors.log'
    with open(log_file, 'w', encoding='utf-8') as log:
        for date, hours in result.items():
            for hour, values in hours.items():
                if len(values['humidity']) < 30:
                    error_message = f"Nicht genug Daten für {date} um {hour} Uhr. Nur {len(values['humidity'])} Daten gefunden.\n"
                    log.write(error_message)


def preparation():
    print("Vorgang wird gestartet.")

    # Dateien laden.
    data = pd.read_csv('evaluation/raw_data/modified_humidity_and_temperature.csv')
    rain = pd.read_csv('evaluation/raw_data/modified_rainfall.csv')

    # Datum und Stunden trennen um sie so später einfacher aufrufen zu können.
    data['datetime'] = pd.to_datetime(data['date'] + ' ' + data['time'])
    data['hour'] = data['datetime'].dt.hour
    data['date'] = data['datetime'].dt.date

    rain['datetime'] = pd.to_datetime(rain['date'] + ' ' + rain['time'])
    rain['hour'] = rain['datetime'].dt.hour
    rain['date'] = rain['datetime'].dt.date

    # Ergebnisstruktur vorbereiten. 
    result = defaultdict(lambda: defaultdict(lambda: {"humidity": [], "temperature": [], "rainfall": 0}))

    # Werte nach Datum und Stunde gruppieren und zusammenfassen.
    for _, row in data.iterrows():
        date = row['date']
        hour = row['hour']
        result[date][hour]['humidity'].append(row['humidity'])
        result[date][hour]['temperature'].append(row['temperature'])
    
    #Durschnittswerte pro Stunde errechnen.
    hourly_data = 'evaluation/results/hourly_data.csv'
    with open(hourly_data, 'w', encoding='utf-8') as csv_file:
        csv_file.write("Date,Hour,Average Temperature(in °C),Average Humidity(in %),Rainfall(mm/m²)\n")
        for date, hours in result.items():
            for hour, values in hours.items():
                error_count(result)  # Fehlerprüfung für jede Stunde
                if values['humidity'] and values['temperature']:
                    avg_humidity = sum(values['humidity']) / len(values['humidity'])
                    avg_temperature = sum(values['temperature']) / len(values['temperature'])
                    result[date][hour]['average_humidity'] = avg_humidity
                    result[date][hour]['average_temperature'] = avg_temperature

     # Regenwerte hinzufügen.
    for _, row in rain.iterrows():
        date = row['date']
        hour = row['hour']
        if date in result and hour in result[date]:
            result[date][hour]['rainfall'] += row['amount']

    # Werte Final zur Weiterverarbeitung in evaluation/results/hourly_data.csv notieren.
    with open(hourly_data, 'a', encoding='utf-8') as csv_file:
        for date, hours in result.items():
            for hour, values in hours.items():
                avg_temperature = values.get('average_temperature', 0)
                avg_humidity = values.get('average_humidity', 0)
                rainfall = values['rainfall']
                if hour<10:
                    csv_file.write(f"{date},0{hour}:00,{avg_temperature},{avg_humidity},{rainfall*136.9863}\n")# rainfall mal 136,9863 rechnen um die Werte auf einen Quadratmeter zukommen.
                else:
                    csv_file.write(f"{date},{hour}:00,{avg_temperature},{avg_humidity},{rainfall*136.9863}\n")
    print("Vorgang wurde erfolgreich abgeschlossen.")

def calculation():
    # Vorhandene Daten laden
    hourly_data_path = 'evaluation/results/hourly_data.csv'
    hourly_data = pd.read_csv(hourly_data_path)
    hourly_data.columns = hourly_data.columns.str.strip()

    # Debug: Überprüfen der geladenen Daten
    print("Geladene hourly_data Spalten:", hourly_data.columns)
    print("Erste Zeilen von hourly_data:\n", hourly_data.head())

    # Neue Daten laden
    forecast = pd.read_csv('csv_data/wetter.csv')
    forecast[['Date', 'Hour']] = forecast['date'].astype(str).str.split(' ', expand=True)
    forecast['Hour'] = forecast['Hour'].str.replace(r'\+.*$', '', regex=True)


    # Werte zusammenführen
    for _, row in forecast.iterrows():
        date = row['date']
        hour = row['hour']
        # Abgleich nach Datum und Stunde
        match = (hourly_data['Date'] == str) & (hourly_data['Hour'] == f"{hour}")
        if any(match):
            idx = hourly_data.index[match][0]
            print(f"Match gefunden: {date} {hour}:00")  # Debug
            hourly_data.at[idx, 'Forecasted Temperature'] = row['Temperatur']
            hourly_data.at[idx, 'Forecasted Humidity'] = row['Luftfeuchtigkeit']
            hourly_data.at[idx, 'Forecasted Rainfall'] = row['Regen'] * 136.9863
        else:
            print(f"Kein Match gefunden: {date} {hour}:00")  # Debug

    # Aktualisierte Daten speichern
    hourly_data.to_csv(hourly_data_path, index=False)
    print("Vorhersagedaten erfolgreich hinzugefügt.")
def main():
    preparation()
    calculation()
main()
