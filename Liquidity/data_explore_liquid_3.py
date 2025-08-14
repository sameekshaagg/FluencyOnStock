import pandas as pd

df = pd.read_csv('Liquidity/liquidity_data_1.csv')

df1 = pd.read_csv('Raw_data/company_name_change.csv')
df1['month_date'] = pd.to_datetime(df1['DATE'], format='%d/%m/%Y').dt.to_period('Q').astype(str)
df1 = df1[['month_date', 'COMNAM', 'TICKER']]

merged_df = pd.merge(df, df1, left_on=['datafqtr', 'tic'], right_on=['month_date', 'TICKER'], how='left')
merged_df = merged_df.rename(columns={"COMNAM": "company_name"})

print(merged_df)
print(merged_df['company_name'].unique())

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
            updated_names.append(row['conml']) 

    group['conml'] = updated_names
    return group

# Apply to each firm
df_updated = (
    merged_df.groupby('tic', group_keys=False)
          .apply(apply_name_changes)
          .reset_index(drop=True)
)
print(len(merged_df), len(df_updated)) 
print(df_updated)

df_updated.to_csv('Liquidity/liquidity_data_2.csv', index=False)

company_name = df_updated['conml'].unique()
pd.DataFrame({'company_name': company_name}).to_csv('Liquidity/company_name_liquidity.csv', index=False)


