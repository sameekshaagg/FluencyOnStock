import tensorflow as tf
from tensorflow import keras
from keras.callbacks import EarlyStopping
from keras.callbacks import ReduceLROnPlateau
import json
import keras_tuner as kt
import pandas as pd
import numpy as np
import random
from sklearn.utils import shuffle
from sklearn.linear_model import LinearRegression

seed = 0
tf.random.set_seed(seed)
np.random.seed(seed)
random.seed(seed)

def prepare_data(df, target_col='count', numeric_cols=None, onehot_cols=None, mean=None, std=None):
    # Drop target and unwanted columns
    df_features = df.drop(columns=[target_col])
    
    # Separate numeric and one-hot features
    X_numeric = df_features[numeric_cols].values
    X_onehot = df_features[onehot_cols].values
    
    y = np.log(y + 1)

    if mean is None or std is None:
        mean = X_numeric.mean(axis=0)
        std = X_numeric.std(axis=0)
    
    epsilon = 1e-8
    X_numeric = (X_numeric - mean) / (std + epsilon)
    
    # Combine back numeric + one-hot
    X = np.hstack([X_numeric, X_onehot])
    
    return X, y, mean, std


df = pd.read_csv('Data_final/merged_frequency_features_big.csv')
df.drop(columns=['freq_score', 'word'], inplace=True)
df = shuffle(df, random_state=0)

df['sound'] = df['sound'].astype(str).str.ljust(4, '0')  # pad with '0' if needed
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

train_size = int(0.7 * len(df))
val_size = int(0.15 * len(df))

train_df = df_model.iloc[:train_size]
val_df = df_model.iloc[train_size:train_size + val_size]
test_df = df_model.iloc[train_size + val_size:]

train_x, train_y, mean, std = prepare_data(train_df, target_col='count', numeric_cols=numeric_cols, onehot_cols=onehot_cols)
val_x, val_y, _, _ = prepare_data(val_df, target_col='count', numeric_cols=numeric_cols, onehot_cols=onehot_cols, mean=mean, std=std)
test_x, test_y, _, _ = prepare_data(test_df, target_col='count', numeric_cols=numeric_cols, onehot_cols=onehot_cols, mean=mean, std=std)

def build_model(hp):
    model = keras.Sequential()
    input_shape = train_x.shape[1]
    
    # input layer
    model.add(keras.Input(shape=(input_shape,), name='Input_Layer'))
    
    for i in range(1, hp.Int("Amount_Of_Hidden_Layers", 1, 6) + 1):
        reg_type = hp.Choice(f'Reg_Type_Layer_{i}', ['none', 'l1', 'l2', 'l1_l2'])
        reg_rate = hp.Choice(f'Reg_Rate_Layer_{i}', [0.0, 0.001, 0.01])
        
        if reg_type == 'none' or reg_rate == 0.0:
            regularizer = None
        elif reg_type == 'l1':
            regularizer = keras.regularizers.l1(reg_rate)
        elif reg_type == 'l2':
            regularizer = keras.regularizers.l2(reg_rate)
        elif reg_type == 'l1_l2':
            regularizer = keras.regularizers.l1_l2(l1=reg_rate, l2=reg_rate)
        model.add(keras.layers.Dense(
            units=hp.Choice(f'Nodes_Layer_{i}', [4, 8, 16, 32]),
            activation=hp.Choice(f'Activation_Layer_{i}', ['relu', 'tanh', 'sigmoid']),
            kernel_regularizer=regularizer,
            name=f'Hidden_Layer_{i}'))
        
        # Add Batch Normalization if selected
        if hp.Boolean(f'BatchNorm_Layer_{i}'):
            model.add(keras.layers.BatchNormalization())

        # Add Dropout if selected
        if hp.Boolean(f'Dropout_Layer_{i}'):
            model.add(keras.layers.Dropout(
                rate=hp.Choice(f'Dropout_Rate_{i}', [0.1, 0.2, 0.3])
            ))
        
    # output layer
    model.add(keras.layers.Dense(1, activation="linear", name='Output_Layer'))
    
    # compiling the model
    learning_rate = hp.Choice("learning_rate", [0.01, 0.001, 0.0001])
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate), 
        loss=keras.losses.Huber(delta=1.0),                                                               
        metrics=[keras.metrics.MeanAbsoluteError(), keras.metrics.MeanSquaredError()])
    
    return model

tuner = kt.Hyperband(
    build_model,
    objective='val_loss',
    max_epochs=20,
    factor=2,
    seed=42,
    directory='my_dir',
    project_name='best_model_huber_log',
    overwrite=False
)

early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=5,
    restore_best_weights=True
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=3,
    min_lr=1e-6,
    verbose=1
)

tuner.search(
    train_x, train_y,
    epochs=25, 
    validation_data=(val_x, val_y),
    batch_size=50, 
    callbacks=[early_stopping, reduce_lr],
    verbose=1
)   
tuner.results_summary()

# Get best model
best_model = tuner.get_best_models(num_models=1)[0]

# View the best hyperparameters
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
print("Best hyperparameters:")
for hp_name in best_hps.values:
    print(f"{hp_name}: {best_hps.get(hp_name)}")
    
# Convert to dictionary
best_hps_dict = {hp: best_hps.get(hp) for hp in best_hps.values}

# Save to JSON
with open('models/best_hyperparameters_huber_log.json', 'w') as f:
    json.dump(best_hps_dict, f, indent=4)

# Evaluate or save the model
best_model.summary()

best_model.save("models/best_model_huber_log.keras", include_optimizer=True)

x_full = np.concatenate([train_x, val_x], axis=0)
y_full = np.concatenate([train_y, val_y], axis=0)

final_model = tuner.hypermodel.build(best_hps)
final_model.fit(
    x_full, y_full,
    epochs=25,
    batch_size=50
)

final_model.save("models/best_model_fit_huber_log.keras", include_optimizer=True)
