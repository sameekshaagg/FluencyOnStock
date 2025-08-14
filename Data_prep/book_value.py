import pandas as pd

df = pd.read_csv("book_value.csv")

print(df.columns)

df['book_value'] = (df['seqq']-df['pstkq'])/(df['cshoq']*df['ajexq'])
print(df)

print(df['book_value'].isna().sum())

df.to_csv("book_value_with_calculation.csv", index=False)

