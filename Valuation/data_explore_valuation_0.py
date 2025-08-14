import pandas as pd

df = pd.read_csv('Valuation/valuation.csv')

#Step one: Merge valuation with company_name_change file
# cols_to_drop = ['atq', 'cogsq', 'cshoq', 'dlttq', 'ltq', 'revtq', 'saleq', 'mkvaltq', 'prccq', 'prchq', 'prclq', 'ggroup', 'gind', 'gsector', 'gsubind', 'busdesc']
# df = df.drop(columns=cols_to_drop, errors='ignore')
print(df.columns)
print(df.head())

df2= pd.read_csv("Raw_data/book_value_with_calculation.csv")
print(df2.columns)

merged = df.merge(
    df2[["datafqtr", "tic", "book_value"]],
    left_on=["datafqtr", "tic"],
    right_on=["datafqtr", "tic"],
    how="left"
)

df = merged
print(df.columns)
print(df.head())

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
# saved as value_NA.csv
# merged.to_csv("value_NA.csv", index=False) 

# Step two: Fill missing company names

merged = merged.drop(columns=['conm', 'costat', 'curcdq', 'datafmt', 'indfmt', 'consol', 'cusip', 'cik', 'busdesc', 'sic', 'spcindcd', 'spcseccd', 'spcsrc', 'fyearq', 'fqtr'], errors='ignore')
#'ggroup', 'gind', 'gsector', 'gsubind',
# Display the first few rows
print(merged.head())
print(merged.columns)
# List of numeric columns to fill missing values in
numeric_cols = ['atq', 'cogsq', 'cshoq', 'dlttq', 'ltq', 'revtq', 'saleq', 'mkvaltq', 'prccq', 'prchq', 'prclq']

# merged[numeric_cols] = (
#     merged.groupby('gvkey')[numeric_cols]
#       .apply(lambda grp: grp.ffill().bfill())
#       .reset_index(level=0, drop=True)  # drop the group key index level to match df index
# )

merged['sales'] = merged['saleq'] / (merged['prccq'] * merged['cshoq'])
merged['profitability'] = (merged['revtq'] - merged['cogsq']) / merged['atq']
merged['leverage'] = merged['dlttq'] / merged['atq']
merged['market_value'] = merged['prccq'] * merged['cshoq']
merged['market_to_book_ratio'] = merged['market_value'] / merged['book_value']
merged = merged.drop(columns=['atq', 'cogsq', 'cshoq', 'dlttq', 'ltq', 'revtq', 'saleq', 'mkvaltq', 'prccq', 'prchq', 'prclq'])
print(merged)
print(merged.columns)

merged = merged.sort_values(['tic', 'datafqtr']).copy()

def apply_name_changes(group):
    # Track the last non-null company_name (i.e., most recent name change)
    current_name = None
    updated_names = []

    for _, row in group.iterrows():
        if pd.notnull(row['company_name']):
            current_name = row['company_name']
        if current_name:
            updated_names.append(current_name)
        else:
            updated_names.append(row['conml'])  # fallback to original conml

    group['conml'] = updated_names
    return group

# Apply to each firm
df_updated = (
    merged.groupby('tic', group_keys=False)
          .apply(apply_name_changes)
          .reset_index(drop=True)
)
print(len(merged), len(df_updated)) 
print(df_updated)
# Save the updated DataFrame to a new CSV file
df_updated.to_csv('Valuation/valuation_1.csv', index=False)
print(df_updated['datafqtr'].min())
print(df_updated['datafqtr'].max())

company_name_A = merged['conml'].unique()
pd.DataFrame({'company_name': company_name_A}).to_csv('Valuation/company_name_valuation.csv', index=False)