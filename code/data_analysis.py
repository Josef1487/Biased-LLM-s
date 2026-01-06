import pandas as pd

df = pd.read_csv(
    r"C:\Users\gabsu\PycharmProjects\Biased-LLM-s\bias_full_permutation_results.csv",
    header=None,
    names=["Szenario", "Name", "Nationalität", "Geschlecht", "Wohnort", "Score"])
#%%
print(df.groupby("Name")["Score"].agg(["mean", "count"]).round(2))
print(df.groupby("Wohnort")["Score"].agg(["mean", "count"]).round(2))