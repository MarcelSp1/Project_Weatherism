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
                if len(values['humidity']) < 29:
                    error_message = f"Nicht genug Daten für {date} um {hour}. Uhr. Nur {len(values['humidity'])} Daten gefunden.\n"
                    log.write(error_message)
                expected_hour += 1
            expected_hour = 0



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
    print("Vorgang wurde erfolgreich abgeschlossen.")

def sorting():
    
    # Vorhandene Daten laden
    hourly_data_path = 'evaluation/results/hourly_data.csv'
    hourly_data = pd.read_csv(hourly_data_path)
    hourly_data.columns = hourly_data.columns.str.strip()

    # Neue Daten laden
    forecast = pd.read_csv('csv_data/forecast.csv')
    forecast['date'] = forecast['date'].str.replace(r'\+.*$', '', regex=True)
    forecast[['Date', 'Hour']] = forecast['date'].astype(str).str.split(' ', expand=True)
    forecast[['gen_date','gen_hour']] = forecast['generated_at'].astype(str).str.split(' ', expand=True)

    sorted = 'evaluation/results/sorted_weather_data.csv'

    print("Beginne mit der Sortierung")

    with open(sorted, 'w', encoding='utf-8') as csv_file: 
        #Hinzufügen der Struktur
        csv_file.write('Date & Time,12 Hours before,11 Hours before,10 Hours before,9 Hours before,8 Hours before,7 Hours before,6 Hours before,5 Hours before,4 Hours before,3 Hours before,2 Hours before,1 Hours before\n')
        
        #Counter damit man später einfacher Zeilenumsprünge setzen kann
        counter = 1
        for _, row in hourly_data.iterrows():
            date = row['Date']
            hour = row['Hour']
            date_time = date+" "+hour
            if (date!='2024-12-27'):
                csv_file.write(f'{date_time},')
                counter=1
            else:
                counter=13
            for _, row in forecast.iterrows():
                #Vorbereiten der Uhrzeit für Späteren Vergleich
                f_date = row['Date']
                f_hour_unfixed = row['Hour']
                f_hour = f_hour_unfixed[:-3]
                gen_hour = row['gen_hour']


                #Daten in einer Variable zusammenfassen für geordnetes runterschreiben
                f_temp = row['temperature']
                f_hum = row['humidity']
                f_rain = row['rain']
                f_data = f'{f_temp} {f_hum} {f_rain}'
                #Wenn das Datum der Vorhersage dem der aktuellen Reihe Stündlicher Werte entspricht, überprüfen ob es der erste wert in der reihe ist
                #Und wenn ja, erst eintragen wenn der erste Wert 12 Stunden vor dem Zeitpunkt ist.
                if f_date == date and f_hour == hour:
                    if counter==1:
                            gen_time = datetime.strptime(gen_hour, "%H:%M:%S.%f")
                            hour_time = datetime.strptime(hour, "%H:%M")
                            difference_time =  hour_time - timedelta(hours=gen_time.hour, minutes=gen_time.minute)
                            difference = difference_time.strftime("%H:%M")
                            if difference == "12:00":
                                csv_file.write(f'{f_data},')
                                counter=counter+1
                    elif counter == 12:
                        csv_file.write(f'{f_data}')
                        counter=1
                        break #Wenn 12 Vorhersage Daten gesammelt wurden wird der Zeilenumbruch gesetz und es geht zur nächsten Stunde.
                    elif counter == 13:
                        break
                    else:
                        csv_file.write(f'{f_data},')
                        counter=counter+1
            if date != '2024-12-27':
                csv_file.write('\n')
    print('Vorgang beendet')

def calculation():
    data = pd.read_csv('evaluation/results/hourly_data.csv')
    forecast = pd.read_csv('evaluation/results/sorted_weather_data.csv')

    evaluated = 'evaluation/results/evaluated_data.csv'
    with open(evaluated, 'w', encoding='utf-8') as csv_file:
        csv_file.write('Date & Time,12 Hours before,11 Hours before,10 Hours before,9 Hours before,8 Hours before,7 Hours before,6 Hours before,5 Hours before,4 Hours before,3 Hours before,2 Hours before,1 Hours before\n')

        for _, rows in forecast.iterrows():
            
            date_time = rows['Date & Time']
            csv_file.write(f'{date_time},')
            for i in range(12):
                time = 12 - i
                forecast[['temperature','humidity','rain']] = forecast[f'{time} Hours before'].str.split(' ', expand=True)


                for _, row in data.iterrows():
                    date = row['Date']
                    hour = row['Hour']
                    d_time = date+" "+hour

                    temp = float(row['Average Temperature(in °C)'])
                    hum = float(row['Average Humidity(in %)'])
                    rain = float(row['Rainfall(in mm)'])

                    if date_time == d_time:
                        #Berechnung der Temperaturunterschiede.
                        f_temp = forecast['temperature'].iloc[i+1]
                        t_difference = temp - float(f_temp)
                        csv_file.write(f'{t_difference} ')


                        #Berechnung der Luftfeuchtigkeitsunterschiede.
                        
                        f_hum = forecast['humidity'].iloc[i+1]
                        hum_difference = hum - float(f_hum)
                        csv_file.write(f'{hum_difference} ')

                        #Berechnung der Regenunterschiede
                        f_rain = forecast['rain'].iloc[i+1]
                        rain_difference = rain - float(f_rain)
                        csv_file.write(f'{rain_difference},')
                
            csv_file.write('\n')

        calculation_data = pd.read_csv('evaluation/results/evaluated_data.csv')
        csv_file.write('Hier folgen die durschnittlichen Werte die, die Vorhersage drüber/drunter lag,,,,,,,,,,,,\n')
        for i in range(12):

            #Bennenung der Variablen für Berechnung
            temp_pos_diff = temp_neg_diff = hum_pos_diff = hum_neg_diff = rain_pos_diff = rain_neg_diff = 0
            avg_temp_pos_diff = avg_temp_neg_diff = avg_hum_pos_diff = avg_hum_neg_diff = avg_rain_pos_diff = avg_rain_neg_diff = 0
            temp_pos = temp_neg = hum_pos = hum_neg = rain_pos = rain_neg = 1

            time = 12 - i
            calculation_data[['temperature','humidity','rain']] = calculation_data[f'{time} Hours before'].fillna('0 0 0').astype(str).str.split(' ', expand=True)

            for _, row in calculation_data.iterrows():
                if row['Date & Time'] != "":
                    temp = float(row['temperature'])

                    if row['humidity'] != "":
                        if row['humidity'] is not None:
                            hum = float(row['humidity'])
                        else:
                            hum = 0
                    else:
                        hum = 0

                    if row['rain'] is not None:
                        rain = float(row['rain'])
                    else:
                        rain = 0.0  # Oder ein anderer Standardwert

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
            if temp_neg!=0:
                avg_temp_neg_diff = (temp_neg_diff/temp_neg)*-1
            if hum_pos!=0:
                avg_hum_pos_diff = (hum_pos_diff/hum_pos)*-1
            if hum_neg!=0:
                avg_hum_neg_diff = (hum_neg_diff/hum_neg)*-1
            if rain_pos!=0:
                avg_rain_pos_diff = (rain_pos_diff/rain_pos)*-1
            if rain_neg!=0:
                avg_rain_neg_diff = (rain_neg_diff/rain_neg)*-1

            #Reinschreiben der durchschnittswerte
            csv_file.write(f'{time}. Stunde vor Zeitpunkt,Temperatur zu hoch:{avg_temp_pos_diff} zu tief:{avg_temp_neg_diff}, Luftfeuchtigkeit zu hoch:{avg_hum_pos_diff}/ zu tief:{avg_hum_neg_diff}, und Regen zu hoch:{avg_rain_pos_diff}/zu tief:{avg_rain_neg_diff},\n')
                


#Average Temperature(in °C),Average Humidity(in %),Rainfall(in mm)
def main():
    #preparation()
    #sorting()
    calculation()
    print('Alles Fertig')
main()