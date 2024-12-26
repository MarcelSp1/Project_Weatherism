import csv
from gpiozero import Button
from datetime import datetime

# Der Niederschlagssensor wird wie ein Knopf behandelt, der jedes Mal bei Kippen der Regenwippe gedrückt wird
# An welchem gpio-Pin der Niederschlagssensor angeschlossen ist, wird in der Variable sensor gespeichert
sensor = Button(6, bounce_time=0.05)

# on_active() fasst zusammen, was bei Aktivierung des Niederschlagssensors passiert
def on_active():
    # Speicher das heutige Datum und dazugehörige Infos in date
    date = datetime.now()
    # Extrahiere nur das Datum aus date
    extracted_date = date.date()
    # Extrahiere nur die Zeit aus date
    time = date.time()
    # amount beschreibt das Volumen der Regenwippe
    amount = 0.2794
    # Fasse das Datum, die Uhrzeit und die Menge in einer Liste mit dem Namen data zusammen
    data = [[extracted_date, time, amount]]
    # Schreibe die Daten in csv_data/rainfall.csv
    with open("/home/marcel/Weatherism/csv_data/rainfall.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)  # Daten schreiben

sensor.when_pressed = on_active
date = datetime.now()
print(date, " System Zwei gestartet.")
while True:
    sensor.wait_for_press()
