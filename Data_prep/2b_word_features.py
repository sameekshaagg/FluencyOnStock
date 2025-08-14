import pandas as pd
import numpy as np
from scipy.stats import spearmanr
import nltk
from nltk.corpus import cmudict
import re
from collections import Counter
from spellchecker import SpellChecker
import phonetics

def average_amount_of_letters(df):
    
    names = df[col_name].to_list()
    container = []
    
    for name in names:
        name = name.lower()
        group = name.split()
        amount_of_words = len(group)
        
        amount_of_letters = 0
        amount_of_letters = sum(
            sum(1 for letter in word if letter.isalpha()) for word in group
        )
        
        average_amount_of_letters = amount_of_letters / amount_of_words if amount_of_words else 0
        container.append(average_amount_of_letters)
    
    return pd.DataFrame(container, columns=['average_amount_of_letters'])

nltk.download('cmudict')
cmu_dict = cmudict.dict()

def count_syllables_nltk(word):
    word = word.lower()
    if word in cmu_dict:
        return [len([ph for ph in pron if ph[-1].isdigit()]) for pron in cmu_dict[word]][0]
    else:
        return estimate_syllables_fallback(word)

def estimate_syllables_fallback(word):
    word = re.sub(r'[^a-z]', '', word.lower())
    vowels = "aeiouy"
    if not word:
        return 0
    count = 0
    if word[0] in vowels:
        count += 1
    for i in range(1, len(word)):
        if word[i] in vowels and word[i - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    return max(count, 1)

def average_amount_of_syllables(df):
    container = []
    for name in df[col_name].fillna('').astype(str).str.lower():
        words = name.split()
        if not words:
            container.append(0)
            continue
        total_syllables = sum(count_syllables_nltk(word) for word in words)
        avg_syllables = total_syllables / len(words)
        container.append(avg_syllables)

    return pd.DataFrame(container, columns=['average_amount_of_syllables'])

def alphabetical_order(df):
    first_letters = df[col_name].str.lower().str[0]

    return pd.DataFrame({
        'abcde': first_letters.isin(list('abcde')).astype(int),
        'middle': first_letters.isin(list('fghijklmnopqrstu')).astype(int),
        'vwxyz': first_letters.isin(list('vwxyz')).astype(int),
    })

def vowel_to_length(df):
    names = df[col_name].astype(str).str.lower().tolist()

    container = []

    for name in names:
        cleaned = re.sub(r'[^a-z]', '', name)
        vowel_count = sum(1 for char in cleaned if char in 'aeiouy')
        total_letters = len(cleaned)
        
        if total_letters == 0:
            container.append(0)
        else:
            container.append(vowel_count / total_letters)

    return pd.DataFrame(container, columns=['vowel_to_length_ratio'])

def most_repetitive_letter(df):
    container = []
    for name in df[col_name].str.lower():
        letters = [ch for ch in name if ch.isalpha()]
        if letters:
            max_count = max(Counter(letters).values())
        else:
            max_count = 0
        container.append(max_count)
    return pd.DataFrame(container, columns=['most repetitions'])

def spell_checker(df):
    spell = SpellChecker()
    # Load your combined word list
    spell.word_frequency.load_text_file('/Users/sameeksha/Desktop/Thesis/words.txt')

    container = []

    for name in df[col_name]:
        words = name.lower().split()
        incorrect = spell.unknown(words)
        container.append(len(incorrect)/len(words) if words else 0)

    return pd.DataFrame(container, columns=['spelling_errors'])

def short_name_flag(df):
    flags = []

    for name in df[col_name]:
        if isinstance(name, str):
            word_count = len(name.split())
            flags.append(1 if word_count <= 2 else 0)
        else:
            flags.append(0)

    return pd.DataFrame(flags, columns=['is_short_name'])

def sound(df):
    soundx = []

    for name in df[col_name]:
        if isinstance(name, str):
            words = name.strip().split()
            if not words:
                soundx.append(None)
                continue

            # Find the longest word (if tie, take the first among them)
            longest_word = max(words, key=len)
            soundex_code = phonetics.soundex(longest_word)

            padded = (soundex_code + '0000')[:4]
            soundx.append(padded)
        else:
            soundx.append(None)

    return pd.DataFrame(soundx, columns=['sound'])

def assembler(df):
    companies = df                                         
    return pd.concat([companies,
                      average_amount_of_letters(df),
                      average_amount_of_syllables(df),
                      alphabetical_order(df),
                      vowel_to_length(df),
                      most_repetitive_letter(df),
                      spell_checker(df), 
                      short_name_flag(df),
                      sound(df)], axis=1)

# Can switch between the two lines below to calculate features for either the frequency list or the company names
col_name = 'company_name'
df = pd.read_csv('Performance/cleaned_company_names_performance.csv')         
assembler(df).to_csv('Performance/company_name_features.csv', index=True, header=True)

# col_name = 'word'
# df = pd.read_csv('Data_final/frequency_big.csv')       
# df = df.drop(columns=['freq_score', 'count'])      
# assembler(df).to_csv('Data_final/frequency_features_big.csv', index=True, header=True)
