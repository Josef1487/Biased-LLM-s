import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# --- PFADE ---
BASE_PATH = r"C:\Development\Development PY\LLM\Biased-LLM-s"
FILE_LEISTUNG = os.path.join(BASE_PATH, "bias_results_LEISTUNG.csv")
FILE_SOZIAL = os.path.join(BASE_PATH, "bias_results_SOZIAL.csv")

# Ausgabe-Pfade
OUT_LEISTUNG = os.path.join(BASE_PATH, "Leistung_Analysis_Stats.png")
OUT_SOZIAL = os.path.join(BASE_PATH, "Sozial_Analysis_Stats.png")

# --- MAPPINGS ---
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

# Mapping für Leistung
scenario_mapping_leistung = {
    "Super": "Academic Performance: Excellent",
    "Mittel": "Academic Performance: Average",
    "Schlecht": "Academic Performance: Poor"
}

# Mapping für Sozial
scenario_mapping_sozial = {
    "Super": "Application with reasonable claim",
    "Mittel": "Application with somewhat reasonable claim",
    "Schlecht": "Application with no reasonable claim",
}


# -----------------------------------------------------------------------------
# HELPER: Funktion zum Hinzufügen der Zahlen
# -----------------------------------------------------------------------------
def add_stat_annotations(g, df, hue_order):
    """
    Fügt statistische Werte (Mean und Range des Fehlerbalkens) hinzu.
    """
    # Wir iterieren über jede Zeile (jedes Szenario-Subplot)
    for ax, (row_name, row_data) in zip(g.axes.flat, df.groupby("Scenario", sort=False)):

        # Berechne Statistiken für dieses Szenario
        stats = row_data.groupby("Name Origin")["Score"].agg(['mean', 'std'])

        # Seaborn 'containers' sind nach Hue (Farbe) sortiert.
        # Container 0 = erste Farbe im hue_order, Container 1 = zweite Farbe, etc.
        for i, container in enumerate(ax.containers):
            # Welcher Herkunft entspricht dieser Container?
            current_origin = hue_order[i]

            # Hole die echten Werte aus der Statistik
            if current_origin in stats.index:
                mean_val = stats.loc[current_origin, 'mean']
                std_val = stats.loc[current_origin, 'std']

                # Falls NaN (z.B. nur 1 Wert), setze SD auf 0
                if pd.isna(std_val): std_val = 0

                lower_bound = max(0, mean_val - std_val)  # Nicht unter 0
                upper_bound = min(100, mean_val + std_val)  # Nicht über 100

                # Text erstellen:
                # Zeile 1: Durchschnitt (Fett)
                # Zeile 2: Range [Von - Bis] (Klein)
                label_text = f"{mean_val:.1f}\n[{lower_bound:.0f}-{upper_bound:.0f}]"
            else:
                label_text = ""

            # Labels an die Balken kleben
            ax.bar_label(
                container,
                labels=[label_text] * len(container),  # Label für jeden Balken im Container
                label_type='edge',  # Am Rand (oben)
                padding=2,  # Abstand zum Balken/Fehlerbalken
                fontsize=7,  # Schriftgröße
                color='black',
                fontweight='normal'  # 'bold' wäre zu dick für den Range
            )

            # OPTIONAL: Damit der Text nicht in den Fehlerbalken rutscht,
            # müssen wir sicherstellen, dass bar_label weiß, wo der Fehlerbalken endet.
            # Da bar_label standardmäßig die Balkenhöhe nimmt, korrigieren wir manuell die Y-Position
            # Das ist kompliziert, daher lassen wir es bei 'padding' und hoffen, es passt.
            # Alternativ: Wir nutzen ax.text() für volle Kontrolle (siehe unten für simple Lösung)


# #############################################################################
# PLOT 1: LEISTUNGSSTIPENDIUM
# #############################################################################

print("--- Verarbeitung: Leistung ---")
df_leistung = pd.read_csv(FILE_LEISTUNG)
df_leistung["Score"] = pd.to_numeric(df_leistung["Score"], errors="coerce").fillna(0)
df_leistung["Evaluation"] = "Current Model"

df_leistung_total = df_leistung.rename(columns=column_mapping)
df_leistung_total["Name Origin"] = df_leistung_total["Name Origin"].str.strip().replace(origin_mapping)
df_leistung_total["Scenario"] = df_leistung_total["Scenario"].replace(scenario_mapping_leistung)

# WICHTIG: Explizite Sortierung für Hue, damit die Labels passen
hue_order_sorted = sorted(df_leistung_total["Name Origin"].unique())

order_scenarios_leistung = [
    "Academic Performance: Excellent",
    "Academic Performance: Average",
    "Academic Performance: Poor"
]

g_leistung = sns.catplot(
    data=df_leistung_total,
    kind="bar",
    x="Evaluation",
    y="Score",
    row="Scenario",
    hue="Name Origin",
    hue_order=hue_order_sorted,  # WICHTIG
    row_order=order_scenarios_leistung,
    legend=True,
    palette="viridis",
    height=5,  # Etwas höher damit Text Platz hat
    aspect=1.8,
    errorbar="sd",  # Standard Deviation als Strich
    sharex=False,
)

# Statistik hinzufügen
add_stat_annotations(g_leistung, df_leistung_total, hue_order_sorted)

# Styling
g_leistung.set_axis_labels("", "Average Score")
for ax, row_name in zip(g_leistung.axes.flat, g_leistung.row_names):
    ax.set_title(row_name, y=-0.16, fontsize=10)
    ax.set_xticklabels([])
    ax.tick_params(bottom=False)
    # Y-Achse etwas erweitern, damit der Text oben nicht abgeschnitten wird
    ax.set_ylim(0, 115)

g_leistung.fig.suptitle(
    'Average Suitability Score for "PLUS-Leistungsstipendium"\n(Mean Score & Variance Range [Low-High])',
    y=0.98, fontsize=14)
g_leistung.fig.subplots_adjust(top=0.90, hspace=0.3, bottom=0.15, left=0.1, right=0.9)

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

# #############################################################################
# PLOT 2: SOZIALSTIPENDIUM
# #############################################################################

print("--- Verarbeitung: Sozial ---")
df_sozial = pd.read_csv(FILE_SOZIAL)
df_sozial["Score"] = pd.to_numeric(df_sozial["Score"], errors="coerce").fillna(0)
df_sozial["Evaluation"] = "Current Model"

df_sozial_total = df_sozial.rename(columns=column_mapping)
df_sozial_total["Name Origin"] = df_sozial_total["Name Origin"].str.strip().replace(origin_mapping)
df_sozial_total["Scenario"] = df_sozial_total["Scenario"].replace(scenario_mapping_sozial)

hue_order_sorted_soc = sorted(df_sozial_total["Name Origin"].unique())

order_scenarios_sozial = [
    "Application with reasonable claim",
    "Application with somewhat reasonable claim",
    "Application with no reasonable claim"
]

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

# Statistik hinzufügen
add_stat_annotations(g_sozial, df_sozial_total, hue_order_sorted_soc)

g_sozial.set_axis_labels("", "Average Score")
for ax, row_name in zip(g_sozial.axes.flat, g_sozial.row_names):
    ax.set_title(row_name, y=-0.16, fontsize=10)
    ax.set_xticklabels([])
    ax.tick_params(bottom=False)
    ax.set_ylim(0, 115)

g_sozial.fig.suptitle('Average Suitability Score for "ÖH-Sozialstipendium"\n(Mean Score & Variance Range [Low-High])',
                      y=0.98, fontsize=14)
g_sozial.fig.subplots_adjust(top=0.90, hspace=0.3, bottom=0.15, left=0.1, right=0.9)

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

print("Fertig! Statistiken wurden hinzugefügt.")