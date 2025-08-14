import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
import tensorflow as tf
from tensorflow import keras
from sklearn.utils import shuffle

seed = 0
tf.random.set_seed(seed)
np.random.seed(seed)

def prepare_data(df, target_col='count', numeric_cols=None, onehot_cols=None, mean=None, std=None):
    # Drop target and unwanted columns
    df_features = df.drop(columns=[target_col])
    
    # Separate numeric and one-hot features
    X_numeric = df_features[numeric_cols].values
    X_onehot = df_features[onehot_cols].values
    
    y = df[target_col].values.astype(np.float32)
    y = np.log(y + 1) 

    if mean is None or std is None:
        mean = X_numeric.mean(axis=0)
        std = X_numeric.std(axis=0)
    
    epsilon = 1e-8
    X_numeric = (X_numeric - mean) / (std + epsilon)
    
    X = np.hstack([X_numeric, X_onehot])
    
    return X, y, mean, std


df = pd.read_csv('Data_final/merged_frequency_features_big.csv')
df.drop(columns=['freq_score'], inplace=True)
df = shuffle(df, random_state=0)

df['sound'] = df['sound'].astype(str).str.ljust(4, '0') 
df['sound_1'] = df['sound'].str[0]
df['sound_2'] = df['sound'].str[1]
df['sound_3'] = df['sound'].str[2]
df['sound_4'] = df['sound'].str[3]

df_onehot = pd.get_dummies(df[['sound_1', 'sound_2', 'sound_3', 'sound_4']], 
                           prefix=['s1', 's2', 's3', 's4'])
df_model = pd.concat([df.drop(columns=['sound', 'sound_1', 'sound_2', 'sound_3', 'sound_4']),
                      df_onehot], axis=1)

numeric_cols = ['Englishness', 'length', 'average_amount_of_letters',
       'average_amount_of_syllables', 'abcde', 'middle', 'vwxyz',
       'vowel_to_length_ratio', 'most repetitions', 'spelling_errors',
       'is_short_name']

onehot_cols = df_onehot.columns.tolist()

train_size = int(0.85 * len(df))
val_size = int(0.15 * len(df))

train_df = df_model.iloc[:train_size]
test_df = df_model.iloc[train_size:]

train_x, train_y, mean, std = prepare_data(train_df, target_col='count', numeric_cols=numeric_cols, onehot_cols=onehot_cols)
test_x, test_y, _, _ = prepare_data(test_df, target_col='count', numeric_cols=numeric_cols, onehot_cols=onehot_cols, mean=mean, std=std)

best_model = keras.models.load_model("models/best_model_fit_huber_log.keras")
print(best_model.summary())
best_model.optimizer.get_config()

n_runs = 100

def evaluate_predictions(true, pred):
    """Compute MAE"""
    mae = mean_absolute_error(true, pred)
    return mae

def huber_loss(y_true, y_pred, delta=1.0):
    error = y_true - y_pred
    is_small_error = np.abs(error) <= delta
    squared_loss = 0.5 * (error ** 2)
    linear_loss = delta * np.abs(error) - 0.5 * delta**2
    return np.mean(np.where(is_small_error, squared_loss, linear_loss))

# Initialize results dictionary
results = {
    "Uniform Distribution Huber": [],
    "Normal Distribution Huber": [],
    "Training Distribution Huber": [],
    "Zipf Distribution Huber": [],
    "OLS Regression Huber": [],
    "Deep Learning Huber": [],
    "Uniform Distribution MAE": [],
    "Normal Distribution MAE": [],
    "Training Distribution MAE": [],
    "Zipf Distribution MAE": [],
    "OLS Regression MAE": [],
}

train_y_orig = np.expm1(train_y)
test_y_orig = np.expm1(test_y)

# Run evaluations
for _ in range(n_runs):
    # Uniform
    preds = np.random.uniform(train_y_orig.min(), train_y_orig.max(), size=len(test_y_orig))
    results["Uniform Distribution Huber"].append(huber_loss(test_y_orig, preds))
    results["Uniform Distribution MAE"].append(evaluate_predictions(test_y_orig, preds))

    # Normal
    preds = np.random.normal(loc=train_y_orig.mean(), scale=train_y_orig.std(), size=len(test_y_orig))
    results["Normal Distribution Huber"].append(huber_loss(test_y_orig, preds))
    results["Normal Distribution MAE"].append(evaluate_predictions(test_y_orig, preds))

    # Training
    preds = np.random.choice(train_y_orig, size=len(test_y_orig), replace=True)
    results["Training Distribution Huber"].append(huber_loss(test_y_orig, preds))
    results["Training Distribution MAE"].append(evaluate_predictions(test_y_orig, preds))

    # Zipf
    zipf_raw = np.random.zipf(a=2.0, size=len(test_y_orig))
    preds = np.interp(zipf_raw, (zipf_raw.min(), zipf_raw.max()), (train_y_orig.min(), train_y_orig.max()))
    results["Zipf Distribution Huber"].append(huber_loss(test_y_orig, preds))
    results["Zipf Distribution MAE"].append(evaluate_predictions(test_y_orig, preds))

# OLS (only once)
ols = LinearRegression()
ols.fit(train_x, train_y_orig)
ols_preds = ols.predict(test_x)
results["OLS Regression Huber"].append(huber_loss(test_y_orig, ols_preds))
results["OLS Regression MAE"].append(evaluate_predictions(test_y_orig, ols_preds))

log_preds = best_model.predict(test_x).flatten()
log_huber = huber_loss(test_y, log_preds, delta=1.0)
log_mae = evaluate_predictions(test_y, log_preds)

true_orig = np.expm1(test_y)
pred_orig = np.expm1(log_preds)
orig_huber = huber_loss(true_orig, pred_orig, delta=1.0)
results["Deep Learning (Huber, log scale)"] = [log_huber]
results["Deep Learning (Huber, original scale)"] = [orig_huber]
orig_mae = evaluate_predictions(true_orig, pred_orig)
results["Deep Learning (MAE, log scale)"] = [log_mae]
results["Deep Learning (MAE, original scale)"] = [orig_mae]

print(f"\nAverage Results over {n_runs} runs:")
for name, scores in results.items():
    if scores:
        print(f"{name:<30} - Avg MAE: {np.mean(scores):.3e}")
    else:
        print(f"{name:<30} - Avg MAE: NaN (no scores)")

x_full = np.concatenate([train_x, test_x], axis=0)
y_full = np.concatenate([train_y, test_y], axis=0)

best_model.fit(
    x_full, y_full,
    epochs=20,
    batch_size=50
)

best_model.save("models/final_model/best_model_all_fit_huber_log.keras", include_optimizer=True)
