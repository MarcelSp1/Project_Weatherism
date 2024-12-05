# Project Weatherism
Project Weatherism ist der Code für die Wetterstation und das Abfragen der Wettervorhersage zugehörig zu P5 von Marcel und Erek.

## read_sensor1.py
**Funktion:** Liest den Temperatursensor alle zwei Minuten aus und notiert die gelesenen Werte in csv_data/humidity_and_temperature.csv
## read_sensor2.py
**Funktion:** Liest dauerhaft den Niederschlagssensor aus und trägt bei dessen Aktivierung die Werte in csv_data/rainfall.csv ein
## write_forecast.py
**Funktion:** Fragt die tägliche Wettervorhersage ab und trägt diese in csv_data/wetter.csv ein

**Ausführung:**
*Die folgenden Befehle in das Terminal eingeben*
1. `cd [PFAD]/Weatherism/`  wechselt in das Verzeichnis von Weatherism. [PFAD] muss gegen den Speicherort des Weatherismordners ausgetauscht werden.
2. `venv\Scripts\activate`      startet das virtual environment.
3. `python write_forecast.py`   führt die write_forecast.py aus.
