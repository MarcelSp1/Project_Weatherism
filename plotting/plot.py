import matplotlib.pyplot as plt
import pandas as pd


def plot_temp(df_temp_hmd, df_forecast):
    colors = [
    '#003f5c',  # Dunkelblau
    '#ff7f0e',  # Orange
    '#2ca02c',  # Grün
    '#d62728',  # Rot
    '#9467bd',  # Lila
    '#8c564b',  # Braun
    '#e377c2',  # Rosa
    '#7f7f7f',  # Grau
    '#bcbd22',  # Gelbgrün
    '#00cc96',  # Hellgrün
    '#f5a623',  # Goldgelb
    '#ff1493']  # Tiefrosa

    for i in range(12):
        plt.figure()
        plt.xlabel('Datum')
        plt.ylabel('Temperatur in °C')
        plt.plot(df_temp_hmd['datetime'], df_temp_hmd['temperature'], marker='o', linestyle='-', ms=4, label='Eigens erfasste Temperaturdaten')

        f_df_forecast = pd.DataFrame(columns=["date", "temperature"])
        f_df_forecast['date'] = pd.to_datetime(df_forecast['Date & Time'])
        
        time = 12 - i
        colors_now = colors[i - 1]
        f_df_forecast['temperature'] = df_forecast[f'{time} Hours before'].str.split().str.get(0).astype('float64')
        plt.title(f'Temperaturverlauf/Vorhersagenälte: {time} Stunden')
        plt.plot(f_df_forecast['date'], f_df_forecast['temperature'], marker='o', color = colors_now, linestyle = '', ms=4, label='Vorhersage für die Temperatur')
        ax = plt.gca()  # Aktuelle Achse abrufen
        plt.xticks(rotation=45)  # Schrägstellen zur besseren Lesbarkeit

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Legende')
        plt.savefig(f'plotting/plot_results/temp_forecast/temp_forecast_{time}_hours_before', bbox_inches='tight')
        plt.close()


def plot_hmd(df_temp_hmd, df_forecast):
    colors = [
    '#003f5c',  # Dunkelblau
    '#ff7f0e',  # Orange
    '#2ca02c',  # Grün
    '#d62728',  # Rot
    '#9467bd',  # Lila
    '#8c564b',  # Braun
    '#e377c2',  # Rosa
    '#7f7f7f',  # Grau
    '#bcbd22',  # Gelbgrün
    '#00cc96',  # Hellgrün
    '#f5a623',  # Goldgelb
    '#ff1493']  # Tiefrosa

    for i in range(12):
        plt.figure()
        plt.xlabel('Datum')
        plt.ylabel('Luftfeuchtigkeit in %')
        plt.plot(df_temp_hmd['datetime'], df_temp_hmd['humidity'], marker='o', linestyle='-', ms=4, label='Eigens erfasste Luftfeuchtigkeitswerte')

        f_df_forecast = pd.DataFrame(columns=["date", "humidity"])
        f_df_forecast['date'] = pd.to_datetime(df_forecast['Date & Time'])
        
        time = 12 - i
        colors_now = colors[i - 1]
        f_df_forecast['humidity'] = df_forecast[f'{time} Hours before'].str.split().str.get(1).astype('float64')
        plt.title(f'Luftfeuchtigkeitsverlauf/Vorhersagenälte: {time} Stunden')
        plt.plot(f_df_forecast['date'], f_df_forecast['humidity'], marker='o', color = colors_now, linestyle = '', ms=4, label='Vorhersage für die Luftfeuchtigkeit')
        ax = plt.gca()  # Aktuelle Achse abrufen
        plt.xticks(rotation=45)  # Schrägstellen zur besseren Lesbarkeit

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Legende')
        plt.savefig(f'plotting/plot_results/hmd_forecast/hmd_forecast_{time}_hours_before', bbox_inches='tight')
        plt.close()

def main():
    print('Starting...')

    df_temp_hmd  = pd.read_csv('evaluation/raw_data/modified_humidity_and_temperature.csv')
    df_temp_hmd['datetime'] = pd.to_datetime(df_temp_hmd['date'] + ' ' + df_temp_hmd['time'])#.dt.strftime('%Y-%m-%d %H:%M:%S')

    df_forecast = pd.read_csv('evaluation/results/sorted_weather_data.csv')

    plot_hmd(df_temp_hmd, df_forecast)
    plot_temp(df_temp_hmd, df_forecast)
    print('Done.')

main()
