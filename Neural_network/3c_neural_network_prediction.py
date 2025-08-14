import tensorflow as tf
from tensorflow import keras
import pandas as pd
import numpy as np
import random
from sklearn.utils import shuffle
import numpy as np

seed = 0
tf.random.set_seed(seed)
np.random.seed(seed)
random.seed(seed)

print(tf.__version__)

def prepare_data_for_inference(df, numeric_cols, onehot_cols, mean, std):
    X_numeric = df[numeric_cols].values
    X_onehot = df[onehot_cols].values

    epsilon = 1e-8
    X_numeric = (X_numeric - mean) / (std + epsilon)

    X = np.hstack([X_numeric, X_onehot])
    return X

# Load new data (company names + features)
# this depends on the previous step on which of valuation, liquidity or performance was chosen
df = pd.read_csv('Performance/merged_company_feature_performance.csv')

# Generate sound features
df['sound'] = df['sound'].astype(str).str.ljust(4, '0')
df['sound_1'] = df['sound'].str[0]
df['sound_2'] = df['sound'].str[1]
df['sound_3'] = df['sound'].str[2]
df['sound_4'] = df['sound'].str[3]

# One-hot encoding for phonetic components
df_onehot = pd.get_dummies(df[['sound_1', 'sound_2', 'sound_3', 'sound_4']], 
                           prefix=['s1', 's2', 's3', 's4'])

# Define columns
onehot_cols = df_onehot.columns.tolist()
drop_cols = ['original_name', 'company_name', 'sound', 'sound_1', 'sound_2', 'sound_3', 'sound_4']
numeric_cols = ['Englishness', 'length', 'average_amount_of_letters',
    'average_amount_of_syllables', 'abcde', 'middle', 'vwxyz',
    'vowel_to_length_ratio', 'most repetitions', 'spelling_errors',
    'is_short_name']

# Calculate mean and std for numeric columns
mean = df[numeric_cols].mean().values
std = df[numeric_cols].std().values
print("Mean:", mean)
print("Std:", std)

# Assemble model-ready dataframe
df_model = pd.concat([df.drop(columns=drop_cols), df_onehot], axis=1)

# Prepare features for prediction
data_x = prepare_data_for_inference(df_model, numeric_cols, onehot_cols, mean, std)

# Load and compile model
best_model = keras.models.load_model('models/final_model/best_model_all_fit_huber_log.keras')

# Predict (model was trained on log1p(target))
preds = best_model.predict(data_x)
# Convert predictions back from log scale
log_preds = np.expm1(preds)

# The file name can be updated as needed
df['predicted_count'] = log_preds
df['predicted_count_log'] = preds
df[['original_name', 'company_name', 'predicted_count', 'predicted_count_log']].to_csv('Performance/trial_check/performance_predictions_huber_log.csv', index=False)
print(df[['company_name', 'predicted_count', 'predicted_count_log']].head())
