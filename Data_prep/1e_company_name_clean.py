import pandas as pd
import re

# Read the CSV file of the company names based on liquidity, performance or valuation
# This file should contain a column named 'company_name' with the names of the companies.
df = pd.read_csv('Performance/company_name_performance.csv')
print(len(df))
df['original_name'] = df['company_name']
df = df[~df['company_name'].isna()]
df = df[~df['company_name'].str.lower().eq('na')]


# Clean and normalize company names
df['company_name'] = (
    df['company_name']
    .str.lower()
    .str.replace(r'\b(ltd|corp|group|plc|inc|limited|holdings?|co|common|stock|corporation|ordinary|shares?|fund|bond|etf)\b', '', regex=True)
    .str.replace(r'\s*\(.*?\)\s*', '', regex=True)  # remove anything in parentheses
    .str.replace(r'\bs\.a\.?\b|\ba/s\b|\bnv\b|\bag\b|\bsa\b|\bp/f\b', '', regex=True)
    .str.replace(r'[^a-zA-Z\s]', '', regex=True)  # remove non-alphabetic characters
    .str.replace(r'\s+', ' ', regex=True)  # collapse multiple spaces
    .str.replace(r'(?<=\b[a-z])\s*&\s*(?=[a-z]\b)', '', regex=True)  
    .str.strip()
)

# Remove names with single-letter words
df = df[~df['company_name'].str.split().apply(lambda x: any(len(word) == 1 for word in x))]
df = df[~df['company_name'].str.contains(r'\d', na=False)]
df = df[df['company_name'].str.contains(r'[a-zA-Z]', na=False)]
df = df[df['company_name'].str.strip() != '']
df = df.dropna(subset=['company_name'])
df = df.drop_duplicates(subset=['company_name'])

df = df[['original_name', 'company_name']]

# Save the cleaned DataFrame to a new CSV file
df.to_csv('Performance/cleaned_company_names_performance.csv', index=False)
print(len(df['company_name'].unique()))
