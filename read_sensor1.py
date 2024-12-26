
import time
import board
import adafruit_dht
import csv
from datetime import datetime

def initialize_device():
    #Den DHT22 initiieren
    try:
        device_port = adafruit_dht.DHT22(board.D2) # D2 gibt den GPiO Pin an
    except Exception as e:
        print(f("Der DHT22 konnte nicht korrekt initialisiert werden. Es gab folgenden Fehler: {e}"))

    return device_port


# Funktion um den Sensor auszulesen
def get_temp_hmd(device_port):
    dhtDevice = device_port
    # Lese den Sensor so lange aus, bis die Daten abgerufen werden können
    while True:
        try:
            # Temperatur in Grad Celsius
            temperature_c = dhtDevice.temperature
            # Luftfeuchtigkeit
            humidity = dhtDevice.humidity
            return temperature_c, humidity

        except RuntimeError as error:
            # Wenn Error: einfach nochmal versuchen (-> schwieriges Auslesen)
            date = datetime.now()
            extracted_date = date.date()
            extracted_time = date.time()
            print(extracted_date, " ", extracted_time, " Es gab einen erwarteten Fehler: ", error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            date = datetime.now()
            extracted_date = date.date()
            extracted_time = date.time()
            print(extracted_date, " ", extracted_time, " Es gab einen unerwarteten Fehler und der Sensor wird verlassen.")
            dhtDevice.exit()
            raise error


# Notiere das Datum, die Zeit, die Luftfeuchtigkeit und die Temperatur in csv_data/humidity_and_temperature.csv
def note_data(temp, hmd):
    temperature, humidity = temp, hmd
    date = datetime.now()
    extracted_date = date.date()
    time = date.time()
    data = [[extracted_date, time, humidity, temperature]]
    with open("/home/marcel/Weatherism/csv_data/humidity_and_temperature.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(data)


# Notiere alle zwei Minuten die dafür ausgelesenen Daten
def main_cycle():
    device_port = initialize_device()
    date = datetime.now()
    print(date, " System Eins gestartet.")
    
    while True:
        if device_port is None:
            initialize_device()
        
        # Einholen des Datums und Extrahierung der Minutenangabe
        prep_time = datetime.now()
        prep_time = prep_time.time()
        prep_time = str(prep_time)
        prep_time = prep_time.split(":")
        time_minute = int(prep_time[1])
        # Ausführung wenn es sich um eine gerade Minute handelt => Ausführung alle zwei Minuten
        if (time_minute % 2 == 0):
            temp, hmd = get_temp_hmd(device_port)
            note_data(temp, hmd)
            time.sleep(110.0)


main_cycle()
