from nltk.stem import WordNetLemmatizer
import nltk
from nltk.corpus import words
import pandas as pd

nltk.download('words')

# Load word list from NLTK and convert to DataFrame
word_list = words.words()
word_list = pd.DataFrame(word_list)

# Convert to lowercase
word_list = word_list[0].str.lower()

# Identify and print removed words (optional but useful)
removed_words = word_list[~word_list.str.match("^[a-zA-Z]+$")]

word_list = word_list[word_list.str.match("^[a-zA-Z]+$")]

lemmatizer = WordNetLemmatizer()
word_list = word_list.apply(lambda x: lemmatizer.lemmatize(x))
word_list = word_list.drop_duplicates().reset_index(drop=True)
print("Lemmatized and Unique Word List Length:", len(word_list))

#Save the final word list to a CSV file
pd.DataFrame(word_list).to_csv("Data_final/data_lexicon.csv", index=False, header=True)







