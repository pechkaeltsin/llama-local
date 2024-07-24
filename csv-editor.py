import pandas as pd


df = pd.read_csv('base_ksr.csv')

df_filtered = df[df['code'].str[0].str.isdigit()]

df_filtered = df_filtered.drop_duplicates(subset='name')

df_filtered.to_csv('ksr.csv', index=False)
