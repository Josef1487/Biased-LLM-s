import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


#%%
df_leistung_phi = pd.read_csv(r"C:\Users\gabsu\PycharmProjects\Biased-LLM-s\Leistung_phi.csv")
df_leistung_qwen = pd.read_csv(r"C:\Users\gabsu\PycharmProjects\Biased-LLM-s\Leistung_qwen.csv")
df_sozial_streng_qwen = pd.read_csv(r"C:\Users\gabsu\PycharmProjects\Biased-LLM-s\Sozial_forcePrompt_qwen.csv")
df_sozial_short_qwen = pd.read_csv(r"C:\Users\gabsu\PycharmProjects\Biased-LLM-s\Sozial_shortPrompt_qwen.csv")
df_sozial_short_phi = pd.read_csv(r"C:\Users\gabsu\PycharmProjects\Biased-LLM-s\Sozial_shortPrompt_phi.csv")
df_sozial_streng_phi = pd.read_csv(r"C:\Users\gabsu\PycharmProjects\Biased-LLM-s\Sozial_forcePrompt_phi.csv")



df_leistung_phi["Model"] = "Phi-3.5-mini-instruct"
df_leistung_qwen["Model"] = "Qwen2.5-3B-Instruct"
df_leistung_gesamt = pd.concat([df_leistung_phi, df_leistung_qwen], ignore_index=True)


#%%

column_mapping = {
    "Szenario": "Scenario",
    "Namensherkunft": "Name Origin",
    "Nationalität": "Nationality",
    "Geschlecht": "Gender",
    "Wohnort": "Location",
    "Score": "Score",
}
df_leistung_total = df_leistung_gesamt.rename(columns=column_mapping)
df_leistung_total["Name Origin"] = df_leistung_total["Name Origin"].str.strip().replace({
    "Türkisch": "Turkish",
    "Englisch(USA)": "US-American",
    "Österreichisch": "Austrian",
    "Kroatisch": "Croatian",
    "Japanisch": "Japanese",
})

df_leistung_total["Scenario"] = df_leistung_total["Scenario"].replace({
    "Super": "Academic Performance: Excellent",
    "Mittel": "Academic Performance: Average",
    "Schlecht": "Academic Performance: Poor"
})

#%%
g_leistung = sns.catplot(
    data=df_leistung_total,
    kind="bar",
    x="Model",
    y="Score",
    row="Scenario",
    hue="Name Origin",
    legend=True,
    palette="viridis",
    height=4.5,
    aspect=1.5,
    errorbar="sd",
    sharex=False,
)
g_leistung.set_axis_labels("", "Average Score")
for ax, row_name in zip(g_leistung.axes.flat, g_leistung.row_names):
    ax.set_title(row_name, y=-0.16, fontsize=10,)
g_leistung.fig.suptitle('Average Suitability Score for "PLUS-Leistungsstipendium"\nby perceived Name Origin',
                        y=0.97, fontsize=14)
g_leistung.fig.subplots_adjust(top=0.92, hspace=0.2, bottom=0.12, left=0.1, right=0.9)

if g_leistung._legend:
    handles = g_leistung._legend.legend_handles
    labels = [t.get_text() for t in g_leistung._legend.texts]

    g_leistung._legend.remove()
    g_leistung._legend = None

    g_leistung.fig.legend(
        handles=handles,
        labels=labels,
        loc='lower center',
        bbox_to_anchor=(0.5, 0.01),
        ncol=2,
        frameon=False,
        fontsize=10
    )
save_path = r"C:\Users\gabsu\PycharmProjects\Biased-LLM-s\Leistung_p1.png"
g_leistung.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()

#%%
df_sozial_short_phi["Prompt"] = "Short Prompt"
df_sozial_streng_phi["Prompt"] = "Explicit Prompt"
df_sozial_phi_total = pd.concat([df_sozial_short_phi, df_sozial_streng_phi], ignore_index=True)
df_sozial_phi_total = df_sozial_phi_total.rename(columns=column_mapping)
df_sozial_phi_total["Name Origin"] = df_sozial_phi_total["Name Origin"].str.strip().replace({
    "Türkisch": "Turkish",
    "Englisch(USA)": "US-American",
    "Österreichisch": "Austrian",
    "Kroatisch": "Croatian",
    "Japanisch": "Japanese",
})
df_sozial_phi_total["Scenario"] = df_sozial_phi_total["Scenario"].replace({
    "Super": "Application with reasonable claim",
    "Mittel": "Application with somewhat reasonable claim",
    "Schlecht": "Application with no reasonable claim",
})

#%%
g_sozial = sns.catplot(
    data=df_sozial_phi_total,
    kind="bar",
    x="Prompt",
    y="Score",
    row="Scenario",
    hue="Name Origin",
    legend=True,
    palette="viridis",
    height=4.5,
    aspect=1.5,
    errorbar="sd",
    sharex=False,
)
g_sozial.set_axis_labels("", "Average Score")
for ax, row_name in zip(g_sozial.axes.flat, g_sozial.row_names):
    ax.set_title(row_name, y=-0.16, fontsize=10,)
g_sozial.fig.suptitle('Average Suitability Score for "ÖH-Sozialstipendium"\nby perceived Name Origin, depending on Prompt complexity\nusing Phi-3.5-mini-instruct',
                        y=0.98, fontsize=14)
g_sozial.fig.subplots_adjust(top=0.92, hspace=0.2, bottom=0.12, left=0.1, right=0.9)

if g_sozial._legend:
    handles = g_sozial._legend.legend_handles
    labels = [t.get_text() for t in g_sozial._legend.texts]

    g_sozial._legend.remove()
    g_sozial._legend = None

    g_sozial.fig.legend(
        handles=handles,
        labels=labels,
        loc='lower center',
        bbox_to_anchor=(0.5, 0.01),
        ncol=2,
        frameon=False,
        fontsize=10
    )
save_path = r"C:\Users\gabsu\PycharmProjects\Biased-LLM-s\Sozial_p1.png"
g_sozial.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()
