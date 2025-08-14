import pandas as pd
import numpy as np
from english_words import get_english_words_set
from nltk.stem import WordNetLemmatizer

# Load the wordlist
word_list = get_english_words_set(['web2', 'gcide'])
word_list = pd.DataFrame(word_list, columns=[0])

print("Original Word List Length:", len(word_list))

# Convert words to lowercase
word_list = word_list[0].str.lower()

# Identify and print removed words (optional but useful)
removed_words = word_list[~word_list.str.match("^[a-zA-Z]+$")]

word_list = word_list[word_list.str.match("^[a-zA-Z]+$")]

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()
word_list = word_list.apply(lambda x: lemmatizer.lemmatize(x))
word_list = word_list.drop_duplicates().reset_index(drop=True)

print("Lemmatized and Unique Word List Length:", len(word_list))

#Save the final word list to a CSV file
pd.DataFrame(word_list).to_csv("Data_final/data_lexicon2.csv", index=False, header=True)
