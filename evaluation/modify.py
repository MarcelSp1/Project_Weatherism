import pandas as pd


def modify_data():
    while True:
        val = input("Wie viele Minuten sollen zu allen Daten hinzugerechnet werden? ")
        try:
            val = int(val)
            break
        except ValueError:
            print("Bitte geben Sie eine ganzahlige Zahl ein.")
    print("Vorgang wird gestartet")
    df = pd.read_csv('csv_data/rainfall2.csv')
    df.to_csv('evaluation/testing/modified_rainfall2.csv', index=False)
    df_mf = pd.read_csv('evaluation/testing/modified_rainfall2.csv')
    temp_datetime = pd.to_datetime(df_mf['date'] + ' ' + df_mf['time'])
    temp_datetime = temp_datetime + pd.Timedelta(minutes = val)
    df_mf['date'] = temp_datetime.dt.date
    df_mf['time'] = temp_datetime.dt.time
    df_mf.to_csv('evaluation/raw_data/modified_rainfall2.csv', index=False)
    print("Vorgang erfolgreich abgeschlossen.")


modify_data()