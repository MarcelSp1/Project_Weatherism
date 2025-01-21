import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('evaluation/raw_data/modified_humidity_and_temperature.csv')
df['datetime'] = pd.to_datetime(df['date'] + ' ' + df['time'])


