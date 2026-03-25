import pandas as pd
from WQI import calculate_wqi

# Combine the 3 CSV files. No data is returned for microseimens.csv
df1 = pd.read_csv('data/milligram.csv')
df2 = pd.read_csv('data/celsius.csv')
df3 = pd.read_csv('data/ntu.csv')

df = pd.concat([df1, df2, df3])

# Convert date
df['ActivityStartDate'] = pd.to_datetime(df['ActivityStartDate'])

# Pivot
df_pivot = df.pivot_table(
    index=['MonitoringLocationID', 'MonitoringLocationLatitude',
           'MonitoringLocationLongitude', 'ActivityStartDate'],
    columns='CharacteristicName',
    values='ResultValue'
).reset_index()

# Rename columns (simplify)
df_pivot.columns.name = None

# Fill missing values with mean
#print(df.isna().sum())
df_pivot = df_pivot.fillna(df_pivot.mean(numeric_only=True))

for index, row in df_pivot.iterrows():
    # calculate_wqi(temp, tss, do, bod=2, cond=160):
    result = calculate_wqi(
        temp=row.get('Temperature, water'),
        tss=row.get('Total suspended solids'),
        do=row.get('Dissolved oxygen (DO)')
    )
    df_pivot.at[index, 'WQI'] = result['WQI']
    df_pivot.at[index, 'Rating'] = result['Rating']

df_pivot.to_csv('data/combined_data.csv', index=False)