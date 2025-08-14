import pandas as pd
import numpy as np

df = pd.read_csv("Liquidity/liquidity_data.csv")


df.drop(columns=['costat', 'curcdq', 'datafmt', 'indfmt', 'consol', 'conm', 'datacqtr', 'mkvaltq', 'cusip'], inplace=True, errors='ignore')

df = df[df['conml'].notna()]
df = df[df['tic'].notna()]
df2 = pd.read_csv("Raw_data/sector_info.csv")
df2.drop(columns=['costat', 'curcdq', 'datafmt', 'indfmt', 'consol', 'fyearq', 'gvkey', 'conml', 'idbflag', 'spcseccd'], inplace=True, errors='ignore')

merged = pd.merge(
    df,
    df2,
    left_on=['tic', 'datafqtr'],
    right_on=['tic', 'datafqtr'],
    how='inner'
)

print(merged.head())
df = merged

df3= pd.read_csv("Raw_data/book_value_with_calculation.csv")
merged = df.merge(
    df3[["datafqtr", "tic", "book_value"]],
    left_on=["datafqtr", "tic"],
    right_on=["datafqtr", "tic"],
    how="left"
)

df = merged
numeric_cols = ['atq', 'cogsq', 'cshoq', 'ltq', 'revtq', 'saleq', 'prccq']

df['market_cap'] = df['prccq'].abs() * df['cshoq']  # In case price is negative
df['size'] = np.log(df['market_cap'])
df['profitability'] = (df['revtq'] - df['cogsq']) / df['atq']
df['price'] = 1 / df['prccq']
df['market_value'] = df['prccq'] * df['cshoq']
df['market_to_book_ratio'] = df['market_value'] / df['book_value']
df = df.drop(columns=['atq', 'cogsq', 'cshoq', 'ltq', 'revtq', 'saleq', 'prccq'])

df1 = pd.read_csv("Liquidity/liquidity_return_2.csv")

# Merge df and df1 on 'tic' <-> 'ticker' and 'datafqtr' <-> 'quarter'
merged = pd.merge(
    df,
    df1,
    left_on=['tic', 'datafqtr'],
    right_on=['Ticker', 'quarter'],
    how='inner'
)

merged.drop(columns=['PERMNO', 'quarter', 'CUSIP', 'Ticker', 'PERMCO', 'IssuerNm'], inplace=True, errors='ignore')
merged.to_csv("Liquidity/liquidity_data_1.csv", index=False)
