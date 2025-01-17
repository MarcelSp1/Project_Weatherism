# **Project Weatherism**
Unter dem Titel Project Weatherism finden sich die, im Zuge von P5 entstandenen, Ergebnisse von Marcel und Erek.
Das umfasst den Code zur Erhebung und Auswertung der Daten sowie die dadurch entstandenen Daten und einen Schaltplan zum Aufbau der Wetterstation.


# Funktionen
## read_sensor1.py
Liest den Temperatursensor alle zwei Minuten aus und notiert die gelesenen Werte in csv_data/humidity_and_temperature.csv.
Wurde zur Ausführung auf dem RPi 4B geschrieben.
## read_sensor2.py
Liest dauerhaft den Niederschlagssensor aus und trägt bei dessen Aktivierung die Werte in csv_data/rainfall.csv ein.
Wurde zur Ausführung auf dem RPi 4B geschrieben.
## write_forecast.py
Fragt die tägliche Wettervorhersage ab und trägt diese in csv_data/weather.csv ein.
Wurde zur Ausführung auf allen Python-unterstützenden Geräten geschrieben und ruft in unserer Konfiguration stündlich die Wettervorhersage für den jeweiligen und nächsten Tag ab.
## evaluation.py
Wertet alle Daten in evaluation/raw_data aus.
Testet bisher nur auf fehlende Daten und errechnet die stündlichen Durchschnitte und fügt Regen werte hinzu (Stand 08.01.2025 21:52 Uhr).
