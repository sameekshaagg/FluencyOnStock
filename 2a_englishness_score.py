import pandas as pd
import numpy as np

df = pd.read_csv('Data_final/frequency_big.csv') 
df = df.drop(columns=['freq_score', 'count'])
list_freq = df['word'].to_list()
print(df.columns)

lexicon = pd.read_csv('/Users/sameeksha/Desktop/Thesis/Data_final/final_lexicon.csv')
lexicon.columns = ['words']
list_lexicon = lexicon['words'].to_list()
print(lexicon.columns)

company_name_list = pd.read_csv('Performance/cleaned_company_names_performance.csv')   
company_name = company_name_list['company_name'].to_list() 

hashed_list = ["#"+str.strip()+"#" for str in list_lexicon]

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '#']

# Generate list of bigrams
bigrams = [a+b for a in letters for b in letters]

trigrams = [a+b+c for a in letters for b in letters for c in letters]

F_bigram = {bigram: 0 for bigram in bigrams}
F_trigram = {trigram: 0 for trigram in trigrams}

def get_bigrams(string):
    bigrams = []

    for i in range(len(string)-1):
        bigram = string[i:i+2]
        bigrams.append(bigram)

    return bigrams

def get_trigrams(string):
    trigrams = []

    for i in range(len(string)-2):
        trigram = string[i:i+3]
        trigrams.append(trigram)

    return trigrams

def count_N_grams(list):
    for word in list:
        bigrams = get_bigrams(word)
        trigrams = get_trigrams(word)
    
        for bigram in bigrams:
            F_bigram[bigram] = F_bigram[bigram] + 1
        for trigram in trigrams:
            F_trigram[trigram] = F_trigram[trigram] + 1
            
count_N_grams(hashed_list)

df_bigrams = pd.DataFrame(list(F_bigram.items()), columns=['bigram', 'count'])
df_bigrams.to_csv('Data_final/data_count_bigrams.csv')
print(df_bigrams)

df_trigrams = pd.DataFrame(list(F_trigram.items()), columns=['trigram', 'count'])
df_trigrams.to_csv('Data_final/data_count_trigrams.csv')
print(df_trigrams)

DF_bigram = dict(zip(df_bigrams['bigram'], df_bigrams['count']))
DF_trigram = dict(zip(df_trigrams['trigram'], df_trigrams['count']))

def get_Englishness_score(word):
    word = '#'+word+'#'
    
    bigrams = get_bigrams(word)
    trigrams = get_trigrams(word)
   
    # specifications
    r = range(1,len(trigrams))
    E = 0
    base = 0.001
    
    # first trigram
    if F_trigram[trigrams[0]] == 0:
        E = E + np.log(base)
    else:
        E = E + np.log(F_trigram[trigrams[0]])
    
    # the other ratios
    for i in r:
        if F_bigram[bigrams[i]] == 0:
            E = E + np.log(base)
        elif trigrams[i] == 'nan':
            E = E + np.log(730 / F_bigram[bigrams[i]])                      
        elif F_trigram[trigrams[i]] == 0:
            E = E + np.log(1 / F_bigram[bigrams[i]])
        else:
            E = E + np.log(F_trigram[trigrams[i]] / F_bigram[bigrams[i]])
    
    return -E

def Englishness_and_length_calculator(list):
    Englishness = []
    length = []
    
    for group in list:
        group = group.lower().split()
        
        E_score = 0
        l_score = 0
        for word in group:
            E_score = E_score + get_Englishness_score(word)
            l_score = l_score + len(word)
        
        Englishness.append(E_score)
        length.append(l_score)
    
    Englishness_df = pd.DataFrame(Englishness, columns=['Englishness'])
    length_df = pd.DataFrame(length, columns=['length'])
    word_df = pd.DataFrame(list, columns=['word'])
        
    merged = pd.concat([word_df, Englishness_df, length_df], axis=1)
    return merged


# Can switch between the two lines below to calculate Englishness for either the frequency list or the company names
# Englishness_and_length_calculator(list_freq).to_csv('Data_final/english_frequency_score_big.csv', index=True, header=True)
Englishness_and_length_calculator(company_name).to_csv('Performance/english_company_score_performance.csv', index=True, header=True)

