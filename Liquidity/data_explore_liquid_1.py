import pandas as pd

df = pd.read_csv("liquidity_return.csv")
# Convert date to datetime
df['date'] = pd.to_datetime(df['DlyCalDt'], format='%d/%m/%Y')
df['quarter'] = df['date'].dt.to_period('Q')
df['abs_return'] = df['DlyRet'].abs()
df['dollar_vol'] = df['DlyPrcVol']
df = df.dropna(subset=['abs_return', 'dollar_vol'])

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
