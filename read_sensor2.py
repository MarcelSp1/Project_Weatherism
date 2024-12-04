import csv
from gpiozero import Button
from datetime import datetime

#Der Niederschlagssensor wird wie ein Knopf behandelt
sensor = Button(6)

def on_active():
    date = datetime.now()
    extracted_date = date.date()
    time = date.time()
    amount = 0.2794
    data = [[extracted_date, time, amount]]
    with open("csv_data/rainfall.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)  # Daten schreiben

sensor.when_pressed = on_active()
sensor.wait_for_press()