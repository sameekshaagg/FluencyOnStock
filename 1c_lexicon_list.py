import pandas as pd

# Load and lowercase all text
lex1 = pd.read_csv('Data_final/data_lexicon.csv')
lex2 = pd.read_csv('Data_final/data_lexicon2.csv')

# Combine the two dataframes
combined = pd.concat([lex1, lex2], ignore_index=True)

# Flatten the dataframe to a list of strings
combined_lex = combined.stack().astype(str).tolist()
combined_lex = list(dict.fromkeys(combined_lex))

# Identify words with non-alphabetic characters (numbers, punctuation, etc.)
non_alpha_words = [word for word in combined_lex if any(not c.isalpha() for c in word)]

# Identify single-letter alphabetic words
single_letter_words = [word for word in combined_lex if isinstance(word, str) and len(word) == 1 and word.isalpha()]

# Remove single-letter words and words with non-alphabetic characters from combined_lex
filtered_lex = [word for word in combined_lex if word not in single_letter_words and word not in non_alpha_words]

# Save the filtered lexicon to a CSV file
filtered_lex_df = pd.DataFrame(filtered_lex, columns=["lexicon_list"])
filtered_lex_df.to_csv('Data_final/final_lexicon.csv', index=False)

