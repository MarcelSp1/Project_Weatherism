# Weatherism

## read_sensor1.py
### Funktion
Liest den Temperatursensor alle zwei Minuten aus und notiert die gelesenen Werte in csv_data/humidity_and_temperature.csv ein

## read_sensor2.py
Liest dauerhaft den Niederschlagssensor aus und trägt bei dessen Aktivierung die Werte in csv_data/rainfall.csv ein

## write_forecast.py 
fragt die tägliche Wettervorhersage ab und trägt diese in csv_data/wetter.csv ein