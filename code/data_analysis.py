import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Pfade konfigurieren
BASE_PATH = r"C:\Development\Development PY\LLM\Biased-LLM-s"
FILE_LEISTUNG = os.path.join(BASE_PATH, "bias_results_LEISTUNG.csv")
FILE_SOZIAL = os.path.join(BASE_PATH, "bias_results_SOZIAL.csv")

OUT_LEISTUNG = os.path.join(BASE_PATH, "Leistung_Analysis_Stats.png")
OUT_SOZIAL = os.path.join(BASE_PATH, "Sozial_Analysis_Stats.png")

# Mappings für Umbenennungen
column_mapping = {
    "Szenario": "Scenario",
    "Namensherkunft": "Name Origin",
    "Nationalität": "Nationality",
    "Geschlecht": "Gender",
    "Wohnort": "Location",
    "Score": "Score",
}

origin_mapping = {
    "Türkisch": "Turkish",
    "Englisch(USA)": "US-American",
    "Österreichisch": "Austrian",
    "Kroatisch": "Croatian",
    "Japanisch": "Japanese",
    "Deutsch": "German",
    "Arabisch": "Arabic"
}

scenario_mapping_leistung = {
    "Super": "Academic Performance: Excellent",
    "Mittel": "Academic Performance: Average",
    "Schlecht": "Academic Performance: Poor"
}

scenario_mapping_sozial = {
    "Super": "Application with reasonable claim",
    "Mittel": "Application with somewhat reasonable claim",
    "Schlecht": "Application with no reasonable claim",
}


# Helfer: Fügt Mean + Std/Range als Text über die Balken
def add_stat_annotations(g, df, hue_order):
    # Iteration durch alle Subplots (Szenarien)
    for ax, (row_name, row_data) in zip(g.axes.flat, df.groupby("Scenario", sort=False)):

        # Stats berechnen (Mean/Std)
        stats = row_data.groupby("Name Origin")["Score"].agg(['mean', 'std'])

        # Durchgehen der Balken-Container (sortiert nach Hue)
        for i, container in enumerate(ax.containers):
            current_origin = hue_order[i]

            if current_origin in stats.index:
                mean_val = stats.loc[current_origin, 'mean']
                std_val = stats.loc[current_origin, 'std']

                if pd.isna(std_val): std_val = 0

                # Range begrenzen (0-100)
                lower_bound = max(0, mean_val - std_val)
                upper_bound = min(100, mean_val + std_val)

                # Label formatieren: Zeile 1 Mean, Zeile 2 Range
                label_text = f"{mean_val:.1f}\n[{lower_bound:.0f}-{upper_bound:.0f}]"
            else:
                label_text = ""

            # Label an Balken heften
            ax.bar_label(
                container,
                labels=[label_text] * len(container),
                label_type='edge',
                padding=2,
                fontsize=7,
                color='black',
                fontweight='normal'
            )


# -----------------------------------------------------------------------------
# 1. Analyse: Leistungsstipendium
# -----------------------------------------------------------------------------
print("--- Verarbeitung: Leistung ---")

# Daten laden & bereinigen
df_leistung = pd.read_csv(FILE_LEISTUNG)
df_leistung["Score"] = pd.to_numeric(df_leistung["Score"], errors="coerce").fillna(0)
df_leistung["Evaluation"] = "Current Model"

# Mappings anwenden
df_leistung_total = df_leistung.rename(columns=column_mapping)
df_leistung_total["Name Origin"] = df_leistung_total["Name Origin"].str.strip().replace(origin_mapping)
df_leistung_total["Scenario"] = df_leistung_total["Scenario"].replace(scenario_mapping_leistung)

# Sortierung für Plots festlegen
hue_order_sorted = sorted(df_leistung_total["Name Origin"].unique())
order_scenarios_leistung = [
    "Academic Performance: Excellent",
    "Academic Performance: Average",
    "Academic Performance: Poor"
]

# Plot generieren
g_leistung = sns.catplot(
    data=df_leistung_total,
    kind="bar",
    x="Evaluation",
    y="Score",
    row="Scenario",
    hue="Name Origin",
    hue_order=hue_order_sorted,
    row_order=order_scenarios_leistung,
    legend=True,
    palette="viridis",
    height=5,
    aspect=1.8,
    errorbar="sd",
    sharex=False,
)

# Annotations hinzufügen
add_stat_annotations(g_leistung, df_leistung_total, hue_order_sorted)

# Achsen & Titel anpassen
g_leistung.set_axis_labels("", "Average Score")
for ax, row_name in zip(g_leistung.axes.flat, g_leistung.row_names):
    ax.set_title(row_name, y=-0.16, fontsize=10)
    ax.set_xticklabels([])
    ax.tick_params(bottom=False)
    ax.set_ylim(0, 115)  # Platz für Labels schaffen

g_leistung.fig.suptitle(
    'Average Suitability Score for "PLUS-Leistungsstipendium"\n(Mean Score & Variance Range [Low-High])',
    y=0.98, fontsize=14)
g_leistung.fig.subplots_adjust(top=0.90, hspace=0.3, bottom=0.15, left=0.1, right=0.9)

# Legende nach unten verschieben
if g_leistung._legend:
    handles = g_leistung._legend.legend_handles
    labels = [t.get_text() for t in g_leistung._legend.texts]
    g_leistung._legend.remove()
    g_leistung._legend = None
    g_leistung.fig.legend(handles=handles, labels=labels, loc='lower center', bbox_to_anchor=(0.5, 0.01), ncol=4,
                          frameon=False, fontsize=10)

print(f"Speichere: {OUT_LEISTUNG}")
g_leistung.savefig(OUT_LEISTUNG, dpi=300, bbox_inches="tight")
plt.close()

# -----------------------------------------------------------------------------
# 2. Analyse: Sozialstipendium
# -----------------------------------------------------------------------------
print("--- Verarbeitung: Sozial ---")

# Daten laden & bereinigen
df_sozial = pd.read_csv(FILE_SOZIAL)
df_sozial["Score"] = pd.to_numeric(df_sozial["Score"], errors="coerce").fillna(0)
df_sozial["Evaluation"] = "Current Model"

# Mappings anwenden
df_sozial_total = df_sozial.rename(columns=column_mapping)
df_sozial_total["Name Origin"] = df_sozial_total["Name Origin"].str.strip().replace(origin_mapping)
df_sozial_total["Scenario"] = df_sozial_total["Scenario"].replace(scenario_mapping_sozial)

hue_order_sorted_soc = sorted(df_sozial_total["Name Origin"].unique())
order_scenarios_sozial = [
    "Application with reasonable claim",
    "Application with somewhat reasonable claim",
    "Application with no reasonable claim"
]

# Plot generieren
g_sozial = sns.catplot(
    data=df_sozial_total,
    kind="bar",
    x="Evaluation",
    y="Score",
    row="Scenario",
    hue="Name Origin",
    hue_order=hue_order_sorted_soc,
    row_order=order_scenarios_sozial,
    legend=True,
    palette="viridis",
    height=5,
    aspect=1.8,
    errorbar="sd",
    sharex=False,
)

# Annotations hinzufügen
add_stat_annotations(g_sozial, df_sozial_total, hue_order_sorted_soc)

# Achsen & Titel anpassen
g_sozial.set_axis_labels("", "Average Score")
for ax, row_name in zip(g_sozial.axes.flat, g_sozial.row_names):
    ax.set_title(row_name, y=-0.16, fontsize=10)
    ax.set_xticklabels([])
    ax.tick_params(bottom=False)
    ax.set_ylim(0, 115)

g_sozial.fig.suptitle('Average Suitability Score for "ÖH-Sozialstipendium"\n(Mean Score & Variance Range [Low-High])',
                      y=0.98, fontsize=14)
g_sozial.fig.subplots_adjust(top=0.90, hspace=0.3, bottom=0.15, left=0.1, right=0.9)

# Legende fixen
if g_sozial._legend:
    handles = g_sozial._legend.legend_handles
    labels = [t.get_text() for t in g_sozial._legend.texts]
    g_sozial._legend.remove()
    g_sozial._legend = None
    g_sozial.fig.legend(handles=handles, labels=labels, loc='lower center', bbox_to_anchor=(0.5, 0.01), ncol=4,
                        frameon=False, fontsize=10)

print(f"Speichere: {OUT_SOZIAL}")
g_sozial.savefig(OUT_SOZIAL, dpi=300, bbox_inches="tight")
plt.close()

print("Fertig.")