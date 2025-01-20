import matplotlib.pyplot as plt
import pandas as pd


df_temp_hmd  = pd.read_csv('evaluation/raw_data/modified_humidity_and_temperature.csv')
df_temp_hmd['datetime'] = pd.to_datetime(df_temp_hmd['date'] + ' ' + df_temp_hmd['time'])#.dt.strftime('%Y-%m-%d %H:%M:%S')

df_forecast = pd.read_csv('evaluation/results/sorted_weather_data.csv')

def plot_temp():
    plt.figure(1)
    plt.title('Temperaturverlauf')
    plt.xlabel('Datum')
    plt.ylabel('Temperatur in °C')
    plt.grid()
    plt.plot(df_temp_hmd['datetime'], df_temp_hmd['temperature'], marker='o', linestyle='')

    f_df_forecast = pd.DataFrame(columns=["date", "temperature"])
    f_df_forecast['date'] = pd.to_datetime(df_forecast['Date & Time'])
    f_df_forecast = f_df_forecast.iloc[:-1]
    for i in range(1):
        time = 12 - i
        f_df_forecast['temperature'] = df_forecast[f'{time} Hours before'].str.split().str.get(0)
        plt.plot(f_df_forecast['date'], f_df_forecast['temperature'], marker='o')
    #print(f_df_forecast.dtypes)
    #print(df_temp_hmd.dtypes)


def plot_hmd():
    plt.figure(2)
    plt.plot(df_temp_hmd['datetime'], df_temp_hmd['humidity'], marker='o', linestyle='')
    plt.title('Temperaturverlauf')
    plt.xlabel('Datum')
    plt.ylabel('Luftfeuchtigkeit in %')
    plt.grid()

def main():
    #plot_hmd()
    plot_temp()
    plt.show()


main()
test