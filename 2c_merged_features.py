import pandas as pd

#Can switch between merging the Englishness score and the features of company names and words from the frequency list

data = pd.read_csv('Performance/english_company_score_performance.csv')
data.drop(columns=['Unnamed: 0'], inplace=True)

feature = pd.read_csv('Performance/company_name_features.csv')
feature.drop(columns=['Unnamed: 0'], inplace=True)

merged_data = pd.merge(feature, data, left_on='company_name', right_on='word', how='inner')
print(merged_data.head())
merged_data.drop(columns=['word'], inplace=True)
merged_data.to_csv('Performance/merged_company_feature_performance.csv', index=False)

# data = pd.read_csv('Data_final/english_frequency_score_big.csv')
# data.drop(columns=['Unnamed: 0'], inplace=True)
# feature = pd.read_csv('Data_final/frequency_features_big.csv')
# feature.drop(columns=['Unnamed: 0'], inplace=True)
# frequency = pd.read_csv('Data_final/frequency_big.csv')

# merged_data = pd.merge(data, feature, left_on='word', right_on='word', how='inner')
# merged_data = pd.merge(merged_data, frequency, left_on='word', right_on='word', how='inner')
# print(merged_data.head())
# merged_data.to_csv('Data_final/merged_frequency_features_big.csv', index=False)

