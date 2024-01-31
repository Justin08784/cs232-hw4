import pandas as pd


df = pd.read_csv("tranco-1m-2024-01-25.csv", header=None)
# topsites
topsites = df.iloc[:1000]
topsites.to_csv("step0-topsites.csv", index=False, header=False)


# othersites
othersites = df.iloc[1999::1000]
othersites.to_csv("step0-othersites.csv", index=False, header=False)