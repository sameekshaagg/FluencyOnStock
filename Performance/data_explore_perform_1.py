import pandas as pd

df = pd.read_csv('Performance/performance_1.csv')
df1 = pd.read_csv('Performance/trial_check/performance_predictions_MSLE_nolog_nol1_l2.csv')

print(df.columns)
print(df1.columns)

df['IssuerNm'] = df['IssuerNm'].str.upper()
df1['original_name'] = df1['original_name'].str.upper()

df.drop(columns=['TICKER', 'company_name'], inplace=True)
df1.drop(columns=['company_name'], inplace=True)


# Merge with suffixes to avoid column name clash
merged_df = pd.merge(df, df1, left_on='IssuerNm', right_on='original_name', how='left', suffixes=('', '_df1'))

# # Drop only the extra columns safely
merged_df = merged_df.drop(columns=['original_name'])

print(merged_df)
unique_conml_count = merged_df['IssuerNm'].nunique()
print(f"Number of unique 'IssuerNm' in merged_df after no prediction: {unique_conml_count}")

# Remove rows where predicted_count is NaN
merged_df = merged_df[~merged_df['predicted_count'].isna()]
unique_conml_count = merged_df['IssuerNm'].nunique()
print(f"Number of unique 'IssuerNm' in merged_df after no prediction: {unique_conml_count}")


month_return = merged_df['MthRet'].isna().sum()
print(f"Number of rows with empty MthRet: {month_return}")
print(merged_df[merged_df['MthRet'].isna()])

# Remove rows where MthRet is NaN
merged_df = merged_df[~merged_df['MthRet'].isna()]
print(merged_df)

unique_conml_count = merged_df['IssuerNm'].nunique()
print(f"Number of unique 'IssuerNm' in merged_df: {unique_conml_count}")

print(merged_df.shape)

merged_df.to_csv('Performance/trial_check/final_data_performance_MSLE_nolog_nol1_l2.csv', index=False)


