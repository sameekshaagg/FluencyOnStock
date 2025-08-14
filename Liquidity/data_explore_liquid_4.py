import pandas as pd

df = pd.read_csv('liquidity_data_2.csv')
df1 = pd.read_csv('Liquidity/trial_check/liquidity_predictions_MAE_nol1_l2.csv')

df['conml'] = df['conml'].str.upper()
df1['original_name'] = df1['original_name'].str.upper()

df.drop(columns=['TICKER', 'company_name', 'month_date'], inplace=True)
df1.drop(columns=['company_name'], inplace=True)


# Merge with suffixes to avoid column name clash
merged_df = pd.merge(df, df1, left_on='conml', right_on='original_name', how='left', suffixes=('', '_df1'))

# # Drop only the extra columns safely
merged_df = merged_df.drop(columns=['original_name'])

print(merged_df)

# Remove rows where predicted_count is NaN
merged_df = merged_df[~merged_df['predicted_count'].isna()]
unique_conml_count = merged_df['conml'].nunique()
print(f"Number of unique 'conml' in merged_df after no prediction: {unique_conml_count}")


empty_mtb_count = merged_df['ILLIQ'].isna().sum()
print(f"Number of rows with empty market_to_book_ratio: {empty_mtb_count}")
print(merged_df[merged_df['market_to_book_ratio'].isna()])

# Remove rows where market_to_book_ratio is NaN
merged_df = merged_df[~merged_df['ILLIQ'].isna()]

unique_conml_count = merged_df['conml'].nunique()
print(f"Number of unique 'conml' in merged_df: {unique_conml_count}")

print(merged_df.shape)

merged_df.to_csv('Liquidity/trial_check/final_data_liquidity_MAE_nol1_l2.csv', index=False)