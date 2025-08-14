import pandas as pd
import re

df = pd.read_csv("Raw_data/word_freq_big.csv")
df['freq_score'] = 1 - (1 / df['count'])
df['word'] = df['word'].str.lower()

# Function to check special characters or single letter
def check_special_or_single_letter(word):
    if pd.isna(word) or not isinstance(word, str):
        return 'Special Character' 
    if len(word) == 1:
        return 'Single Letter'
    elif re.search(r'[^a-zA-Z0-9]', word):  
        return 'Special Character'
    else:
        return 'Normal'

# Apply function to the 'word' column
df['check'] = df['word'].apply(check_special_or_single_letter)

df_single_letter = df[df['check'] == 'Single Letter']
df_special_character = df[df['check'] == 'Special Character']
df_normal = df[df['check'] == 'Normal']

df_normal = df_normal.drop(columns=['check'])
pd.DataFrame(df_normal).to_csv("Data_final/frequency_big.csv", index=False, header=True)

