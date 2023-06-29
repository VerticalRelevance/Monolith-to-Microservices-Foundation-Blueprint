import pandas as pd

with open('USCities.json', encoding='utf-8') as inputfile:
    df = pd.read_json(inputfile)

df.to_csv('USCities.csv', encoding='utf-8', index=False)