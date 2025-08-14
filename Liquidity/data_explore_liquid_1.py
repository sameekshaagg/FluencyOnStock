import pandas as pd

import pandas as pd

df = pd.read_csv("liquidity_return.csv")
print(df.columns)
print(df.head())

# Convert date to datetime
df['date'] = pd.to_datetime(df['DlyCalDt'], format='%d/%m/%Y')

# Add quarter and year columns
df['quarter'] = df['date'].dt.to_period('Q')

# Absolute returns
df['abs_return'] = df['DlyRet'].abs()

# Add dollar volume (price * volume)
df['dollar_vol'] = df['DlyPrcVol']

# Drop rows with missing dollar volume or return
df = df.dropna(subset=['abs_return', 'dollar_vol'])

# Calculate illiquidity per firm-quarter
illiq = df.groupby(['PERMNO', 'quarter']).apply(
    lambda g: pd.Series({
        'ILLIQ': (g['abs_return'] / g['dollar_vol']).mean(),
        'Ticker': g['Ticker'].iloc[0],
        'PERMCO': g['PERMCO'].iloc[0],
        'IssuerNm': g['IssuerNm'].iloc[0]
    })
).reset_index()

vol = df.groupby(['PERMNO', 'quarter'])['DlyRet'].std().reset_index(name='Volatility')

avg_price = df.groupby(['PERMNO', 'quarter'])['DlyPrc'].mean().reset_index(name='AvgPrice')

num_days = df.groupby(['PERMNO', 'quarter']).size().reset_index(name='NumDays')

# Start from ILLIQ
metrics = illiq.merge(vol, on=['PERMNO', 'quarter'], how='left')
metrics = metrics.merge(avg_price, on=['PERMNO', 'quarter'], how='left')
metrics = metrics.merge(num_days, on=['PERMNO', 'quarter'], how='left')


print(metrics.head())

metrics.to_csv("liquidity_return_2.csv", index=False)