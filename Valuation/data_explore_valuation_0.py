import pandas as pd

df = pd.read_csv('Valuation/valuation.csv')

df2= pd.read_csv("Raw_data/book_value_with_calculation.csv")

merged = df.merge(
    df2[["datafqtr", "tic", "book_value"]],
    left_on=["datafqtr", "tic"],
    right_on=["datafqtr", "tic"],
    how="left"
)

df = merged
file_path1 = 'Raw_data/company_name_change.csv'
cols_to_drop1 = ['HSICMG', 'HSICIG', 'SHRCLS', 'NAMEENDT', 'SHRCD', 'EXCHCD', 'SICCD', 'NAICS', 'PRIMEXCH', 'TRDSTAT']
df1 = pd.read_csv(file_path1)
df1 = df1.drop(columns=cols_to_drop1, errors='ignore')
df1["DATE"] = df1["DATE"].astype(str).str.strip() 
df1["DATE"] = df1["DATE"].str.replace(r"[^0-9/]", "", regex=True)
df1["DATE"] = pd.to_datetime(df1["DATE"], dayfirst=True, errors="coerce")
df1["yearquarter"] = df1["DATE"].dt.to_period("Q").astype(str)

common_tickers = set(df['tic']).intersection(set(df1['TICKER']))

merged = df.merge(
    df1[["yearquarter", "TICKER", "COMNAM"]],
    left_on=["datafqtr", "tic"],
    right_on=["yearquarter", "TICKER"],
    how="left"
)

# Rename COMNAM to company_name
merged = merged.rename(columns={"COMNAM": "company_name"})

merged = merged.drop(columns=['conm', 'costat', 'curcdq', 'datafmt', 'indfmt', 'consol', 'cusip', 'cik', 'busdesc', 'sic', 'spcindcd', 'spcseccd', 'spcsrc', 'fyearq', 'fqtr'], errors='ignore')

merged['sales'] = merged['saleq'] / (merged['prccq'] * merged['cshoq'])
merged['profitability'] = (merged['revtq'] - merged['cogsq']) / merged['atq']
merged['leverage'] = merged['dlttq'] / merged['atq']
merged['market_value'] = merged['prccq'] * merged['cshoq']
merged['market_to_book_ratio'] = merged['market_value'] / merged['book_value']
merged = merged.drop(columns=['atq', 'cogsq', 'cshoq', 'dlttq', 'ltq', 'revtq', 'saleq', 'mkvaltq', 'prccq', 'prchq', 'prclq'])

merged = merged.sort_values(['tic', 'datafqtr']).copy()

def apply_name_changes(group):
    current_name = None
    updated_names = []

    for _, row in group.iterrows():
        if pd.notnull(row['company_name']):
            current_name = row['company_name']
        if current_name:
            updated_names.append(current_name)
        else:
            updated_names.append(row['conml']) 

    group['conml'] = updated_names
    return group

df_updated = (
    merged.groupby('tic', group_keys=False)
          .apply(apply_name_changes)
          .reset_index(drop=True)
)

df_updated.to_csv('Valuation/valuation_1.csv', index=False)
print(df_updated['datafqtr'].min())
print(df_updated['datafqtr'].max())

company_name_A = merged['conml'].unique()
pd.DataFrame({'company_name': company_name_A}).to_csv('Valuation/company_name_valuation.csv', index=False)
