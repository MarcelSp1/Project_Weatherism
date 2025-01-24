import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta

# Werte pro Stunde zählen.
# Falls keine 30 vorhanden sind, wird dies in evaluation/results/errors.log vermerkt.
def error_count(result):
    log_file = 'evaluation/results/errors.log'
    with open(log_file, 'w', encoding='utf-8') as log:
        expected_hour = 12
        # Iterierung durch die Daten
        for date, hours in result.items():
            # Iterierung durch die Stunden pro Datum
            for hour, values in hours.items():
                # Überprüfung, ob eine oder mehrere Stunden fehlen
                while expected_hour < hour:
                    error_message = f"Keine Daten für {date} {expected_hour}. Uhr.\n"
                    log.write(error_message)
                    expected_hour += 1
                # Überprüfung, ob die 30 Daten der Stunde komplett sind
                if len(values['humidity']) < 30:
                    error_message = f"Nicht genug Daten für {date} um {hour}. Uhr. Nur {len(values['humidity'])} Daten gefunden.\n"
                    log.write(error_message)
                expected_hour += 1
            expected_hour = 0

def preparation():
    print("Stündliche Durschnitte werden berechnet.")

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
    result = defaultdict(lambda: defaultdict(lambda: {"humidity": [], "temperature": [], "rainfall": 0.0}))

    # Werte nach Datum und Stunde gruppieren und zusammenfassen.
    for _, row in data.iterrows():
        date = row['date']
        hour = row['hour']
        result[date][hour]['humidity'].append(row['humidity'])
        result[date][hour]['temperature'].append(row['temperature'])
    
    #Durschnittswerte pro Stunde errechnen.
    hourly_data = 'evaluation/results/hourly_data.csv'
    with open(hourly_data, 'w', encoding='utf-8') as csv_file:
        csv_file.write("Date,Hour,Average Temperature(in °C),Average Humidity(in %),Rainfall(in mm)\n")
        for date, hours in result.items():
            for hour, values in hours.items():
                error_count(result)  # Fehlerprüfung für jede Stunde
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
                    csv_file.write(f"{date},0{hour}:00,{avg_temperature},{avg_humidity},{rainfall}\n")# rainfall mal 136,9863 rechnen um die Werte auf einen Quadratmeter zukommen.
                else:
                    csv_file.write(f"{date},{hour}:00,{avg_temperature},{avg_humidity},{rainfall}\n")
    print("Berechnung abgeschlossen.")

def sorting(): 
    print('Vorhersagedaten werden sortiert.')

    # Reale Daten laden
    hourly_data_path = 'evaluation/results/hourly_data.csv'
    hourly_data = pd.read_csv(hourly_data_path)
    hourly_data['Datetime'] = pd.to_datetime(hourly_data['Date']+' '+hourly_data['Hour'])

    # Vorhersagedaten laden
    forecast = pd.read_csv('evaluation/raw_data/modified_forecast.csv')
    forecast['generated_at'] = pd.to_datetime(forecast['generated_at'])
    forecast['generated_at'] = forecast['generated_at'].dt.strftime('%Y-%m-%d %H:%M:%S')
    forecast['generated_at'] = pd.to_datetime(forecast['generated_at'])
    forecast['generated_at'] = forecast['generated_at'].apply(lambda x: x.replace(minute=0, second=0))
    forecast['date'] = forecast['date'].str.slice(0, -6)
    forecast['date'] = pd.to_datetime(forecast['date'])

    # Ergebnisdatei
    sorted = 'evaluation/results/sorted_weather_data.csv'

    result = pd.DataFrame(columns=['Datetime','12 Hours before','11 Hours before','10 Hours before','9 Hours before','8 Hours before','7 Hours before','6 Hours before','5 Hours before','4 Hours before','3 Hours before','2 Hours before','1 Hours before'])
    result['Datetime'] = pd.to_datetime(hourly_data['Datetime'])

    # Daten sortieren
    for _, row in result.iterrows():
        date = pd.to_datetime(row['Datetime'])
        gen_date = pd.Timestamp(date)

        for i in range(12):
            gen_date = gen_date - pd.Timedelta(hours=12-i)
            col = f'{12-i} Hours before'

            # Zeile finden, die beide Bedingungen erfüllt
            forecast_row = forecast.loc[(forecast['generated_at'] == gen_date) & (forecast['date'] == date)]
            # Werte in Variablen speichern
            if not forecast_row.empty:
                temperature = forecast_row['temperature'].values[0]
                humidity = forecast_row['humidity'].values[0]
                rain = forecast_row['rain'].values[0]
            
            data = f'{temperature} {humidity} {rain}'
            result.loc[result['Datetime'] == date,[col]] = data
    result.to_csv(sorted, index=False)
    print('Sortierung abgeschlossen.')

def calculation():
    print('Abweichungen werden berechnet.')
    #Einpflegen der Datein
    data = pd.read_csv('evaluation/results/hourly_data.csv')
    forecast = pd.read_csv('evaluation/results/sorted_weather_data.csv')
    evaluated = 'evaluation/results/evaluated_data.csv'

    with open(evaluated, 'w', encoding='utf-8') as csv_file:
        #Struktur erstellen
        csv_file.write('Date & Time,12 Hours before,11 Hours before,10 Hours before,9 Hours before,8 Hours before,7 Hours before,6 Hours before,5 Hours before,4 Hours before,3 Hours before,2 Hours before,1 Hours before,\n')
        count_row = 0
        for _, rows in forecast.iterrows():
            
            date_time = rows['Datetime']
            csv_file.write(f'{date_time},')

            #Ausführung für alle 12 Vorhersage Spalten
            for i in range(12):
                time = 12 - i
                #Vorhersage Daten trennen damit man mit diesen einfacher seperate Differenzen errechnen kann.
                forecast[[f'{time}_temperature',f'{time}_humidity',f'{time}_rain']] = forecast[f'{time} Hours before'].str.split(' ', expand=True)

                for _, row in data.iterrows():
                    #Daten aus den gemessenen Daten einpflegen.
                    date = row['Date']
                    hour = row['Hour']
                    d_time = date+" "+hour
                    
                    #Umwandlung der Daten in floats um damit zu rechnen
                    temp = float(row['Average Temperature(in °C)'])
                    hum = float(row['Average Humidity(in %)'])
                    rain = float(row['Rainfall(in mm)'])

                    if date_time == d_time:
                        #Berechnung der Temperaturunterschiede.
                        f_temp = forecast[f'{time}_temperature'].iloc[count_row]
                        t_difference = temp - float(f_temp)
                        csv_file.write(f'{t_difference} ')

                        #Berechnung der Luftfeuchtigkeitsunterschiede.
                        f_hum = forecast[f'{time}_humidity'].iloc[count_row]
                        hum_difference = hum - float(f_hum)
                        csv_file.write(f'{hum_difference} ')

                        #Berechnung der Regenunterschiede
                        f_rain = forecast[f'{time}_rain'].iloc[count_row]
                        rain_difference = rain - float(f_rain)
                        csv_file.write(f'{rain_difference},')
            count_row = count_row+1
            csv_file.write('\n')

        calculation_data = pd.read_csv('evaluation/results/evaluated_data.csv')
        csv_file.write('Hier folgen die durschnittlichen Werte die, die Vorhersage drüber/drunter lag,,,,,,,,,,,,\n')

        avg_avg_temp_pos_diff = 0
        avg_avg_temp_neg_diff = 0
        avg_avg_hum_pos_diff = 0
        avg_avg_hum_neg_diff = 0
        avg_avg_rain_pos_diff = 0
        avg_avg_rain_neg_diff = 0

        for i in range(12):

            #Bennenung der Variablen für Berechnung
            temp_pos_diff = temp_neg_diff = hum_pos_diff = hum_neg_diff = rain_pos_diff = rain_neg_diff = 0
            avg_temp_pos_diff = avg_temp_neg_diff = avg_hum_pos_diff = avg_hum_neg_diff = avg_rain_pos_diff = avg_rain_neg_diff = 0
            temp_pos = temp_neg = hum_pos = hum_neg = rain_pos = rain_neg = 0

            time = 12 - i
            calculation_data[[f'{time}_temperature',f'{time}_humidity',f'{time}_rain']] = calculation_data[f'{time} Hours before'].astype(str).str.split(' ', expand=True)

            for _, row in calculation_data.iterrows():
                #Debugging Line so it works even when something is missing
                if row['Date & Time'] != "":

                    #Umwandeln zum rechnen inklusive Debugging
                    if row[f'{time}_temperature'] is not None:
                        temp = float(row[f'{time}_temperature'])

                    if row[f'{time}_humidity'] is not None:
                        hum = float(row[f'{time}_humidity'])

                    if row[f'{time}_rain'] is not None:
                        rain = float(row[f'{time}_rain'])

                    #Sortieren der Differenzen in zu hoch oder zu tief
                    if temp < 0:
                        temp_pos_diff += temp
                        temp_pos+=1
                    elif temp > 0:
                        temp_neg_diff += temp
                        temp_neg+=1
                    
                    if hum < 0:
                        hum_pos_diff += hum
                        hum_pos+=1
                    elif hum > 0:
                        hum_neg_diff += hum
                        hum_neg=hum_neg+1

                    if rain < 0:
                        rain_pos_diff += rain
                        rain_pos+=1
                    elif rain > 0:
                        rain_neg_diff += rain
                        rain_neg+=1
            
            #Berechnen der durchschnittlichen differenz
            if temp_pos!=0:
                avg_temp_pos_diff = (temp_pos_diff/temp_pos)*-1
                avg_avg_temp_pos_diff += avg_temp_pos_diff
            if temp_neg!=0:
                avg_temp_neg_diff = (temp_neg_diff/temp_neg)*-1
                avg_avg_temp_neg_diff += avg_temp_neg_diff
            if hum_pos!=0:
                avg_hum_pos_diff = (hum_pos_diff/hum_pos)*-1
                avg_avg_hum_pos_diff += avg_hum_pos_diff
            if hum_neg!=0:
                avg_hum_neg_diff = (hum_neg_diff/hum_neg)*-1
                avg_avg_hum_neg_diff += avg_hum_neg_diff
            if rain_pos!=0:
                avg_rain_pos_diff = (rain_pos_diff/rain_pos)*-1
                avg_avg_rain_pos_diff += avg_rain_pos_diff
            if rain_neg!=0:
                avg_rain_neg_diff = (rain_neg_diff/rain_neg)*-1
                avg_avg_rain_neg_diff += avg_rain_neg_diff

            #Reinschreiben der durchschnittswerte
            csv_file.write(f'{time} Stunden vor Zeitpunkt:,Temperatur zu hoch:{avg_temp_pos_diff} | zu tief:{avg_temp_neg_diff},Luftfeuchtigkeit zu hoch:{avg_hum_pos_diff} | zu tief:{avg_hum_neg_diff},Regen zu hoch:{avg_rain_pos_diff} | zu tief:{avg_rain_neg_diff},,,,,,,,,,\n')
        csv_file.write(f'Overall durchschnittliche Abweichung:,Temperatur zu hoch:{avg_avg_temp_pos_diff/12} | zu tief:{avg_avg_temp_neg_diff/12},Luftfeuchtigkeit zu hoch:{avg_avg_hum_pos_diff/12} | zu tief:{avg_avg_hum_neg_diff/12},Regen zu hoch:{avg_avg_rain_pos_diff/12} | zu tief:{avg_avg_rain_neg_diff/12},,,,,,,,,,\n')
                
def main():
    preparation()
    sorting()
    calculation()
    print('Alles Fertig. Ergebnisse finden sich in evaluation/results/evaluated_data.csv')
main()