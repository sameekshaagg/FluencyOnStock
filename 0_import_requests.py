import pandas as pd

# used to download the English word frequency list from Hugging Face
# Login using e.g. `huggingface-cli login` to access this dataset
df = pd.read_parquet("hf://datasets/g2p-exploration/english-word-frequency-list/data/train-00000-of-00001.parquet")
df.to_csv("word_freq_big.csv", index=False)
