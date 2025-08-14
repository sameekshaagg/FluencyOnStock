import pandas as pd

df = pd.read_csv('Raw_data/performance.csv')
df = df.drop(columns = ['HdrCUSIP', 'SecurityNm', 'ICBIndustry', 'MthPrcDt']) 

df['month_date'] = pd.to_datetime(df['MthCalDt'], format='%d/%m/%Y').dt.strftime('%m_%Y')
df['quarter_date'] = pd.to_datetime(df['MthCalDt'], format='%d/%m/%Y').apply(lambda x: f"{x.year}Q{x.quarter}")

df2 = pd.read_csv('Raw_data/sector_info.csv')
df2 = df2.drop(columns = ['costat', 'curcdq','datafmt','indfmt','consol', 'fyearq','gvkey','conml', 'idbflag','spcseccd'])
 
merged_df = pd.merge(df, df2, left_on=['quarter_date', 'Ticker'], right_on=['datafqtr', 'tic'], how='left')

merged_df = merged_df.drop(columns=['tic', 'datafqtr'])
df = merged_df

df3 = pd.read_csv('Liquidity/liquidity_data_2.csv')
df3 = df3.drop(columns = ['datadate', 'gvkey','conml','book_value','market_value', 'market_to_book_ratio','ILLIQ','Volatility', 'NumDays','month_date', 'company_name', 'TICKER'])

merged_df = pd.merge(df, df3, left_on=['quarter_date', 'Ticker'], right_on=['datafqtr', 'tic'], how='left')
df = merged_df

df1 = pd.read_csv('Raw_data/company_name_change.csv')
df1['month_date'] = pd.to_datetime(df1['DATE'], format='%d/%m/%Y').dt.strftime('%m_%Y')
df1 = df1[['month_date', 'COMNAM', 'TICKER']]

merged_df = pd.merge(df, df1, left_on=['month_date', 'Ticker'], right_on=['month_date', 'TICKER'], how='left')
merged_df = merged_df.rename(columns={"COMNAM": "company_name"})

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
            updated_names.append(row['IssuerNm']) 

    group['IssuerNm'] = updated_names
    return group

# Apply to each firm
df_updated = (
    merged_df.groupby('Ticker', group_keys=False)
          .apply(apply_name_changes)
          .reset_index(drop=True)
)

df_updated.to_csv('Performance/performance_1.csv', index=False)

company_name = df_updated['IssuerNm'].unique()
pd.DataFrame({'company_name': company_name}).to_csv('Performance/company_name_performance.csv', index=False)

