import pandas as pd
import matplotlib.pyplot as plt

# Stichprobentag definieren
date = '2025-01-13'

# Für Temperatur oder Luftfeuchtigkeit
choice = 'humidity'

# Ursprüngliche Daten einlesen
df = pd.read_csv('evaluation/raw_data/modified_humidity_and_temperature.csv')

# Datum vorbereiten
df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'])

# Daten für den Stichprobentag herrausfiltern
df_filtered = df[df['timestamp'].dt.date == pd.to_datetime(date).date()]

# Extrahierung der Stunde für die Gruppierung
df_filtered['hour'] = df_filtered['timestamp'].dt.hour

# Boxplot-Diagramm erstellen
df_filtered.boxplot(column= choice , by='hour', grid=False)

# Diagramm formatieren
plt.title(f'Stündliche Boxplots für den {date}')
plt.suptitle('')
plt.xlabel('Stunde des Tages')
if choice == 'temperature':
    plt.ylabel('Temperatur in °C')
else:
    plt.ylabel('Luftfeuchtigkeit in %')

plt.xticks(range(25), [f'{h-1}:00' for h in range(25)])  # Beschriftung der X-Achse
current_xticks, _ = plt.xticks()
plt.xticks(current_xticks + 1) # Beschriftung der X-Achse um eins nach rechts verschieben
plt.xticks(rotation=45)  # Beschriftung der X-Achse um 45 Grad drehen

plt.savefig(f'plotting/plot_results/daily_boxplots/{choice}/{date}.png')
