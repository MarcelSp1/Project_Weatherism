from datetime import datetime
import pandas as pd

def copy_csv():
    df = pd.read_csv('csv_data/humidity_and_temperature.csv')
    df.to_csv('evaluation/testing/modified_humidity_and_temperature.csv')

def main():
    while True:
        val = input("Wie viele Minuten sollen zu allen Daten hinzugerechnet werden? ")
        try:
            val = int(val)
            break
        except ValueError:
            print("Bitte geben Sie eine ganzahlige Zahl ein.")
    print("Vorgang wird gestartet")
    copy_csv()
    df_mf = pd.read_csv('evaluation/testing/modified_humidity_and_temperature.csv')
    temp_date = pd.to_datetime(df_mf['date'] + ' ' + df_mf['time'])
    print(temp_date)
    temp_date = temp_date + pd.Timedelta(minutes = val)
    print(temp_date)

main()