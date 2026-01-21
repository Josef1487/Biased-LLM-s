import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# --- KONFIGURATION ---
BASE_PATH = r"C:\Development\Development PY\LLM\Biased-LLM-s"
FILE_SOZIAL = os.path.join(BASE_PATH, "bias_results_SOZIAL.csv")
FILE_LEISTUNG = os.path.join(BASE_PATH, "bias_results_LEISTUNG.csv")

# Ausgabe-Ordner
OUTPUT_IMG_PATH = os.path.join(BASE_PATH, "plots")
os.makedirs(OUTPUT_IMG_PATH, exist_ok=True)

# Design
sns.set_theme(style="whitegrid", context="talk")
PALETTE_GENDER = "pastel"
PALETTE_ORIGIN = "husl"


def load_and_clean_data(filepath):
    """Lädt CSV, bereinigt Strings und prüft auf Fehler."""
    if not os.path.exists(filepath):
        print(f"WARNUNG: Datei nicht gefunden: {filepath}")
        return None

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"FEHLER beim Lesen von {filepath}: {e}")
        return None

    if df.empty:
        print(f"WARNUNG: Datei {filepath} ist leer (nur Header?).")
        return None

    # --- DEBUGGING INFO ---
    print(f"\n--- LADE DATEN: {os.path.basename(filepath)} ---")
    print(f"Spalten gefunden: {list(df.columns)}")
    print(f"Anzahl Zeilen: {len(df)}")

    # 1. Strings bereinigen (Leerzeichen entfernen)
    # Das ist der häufigste Fehler: " Super " != "Super"
    for col in ["Szenario", "Geschlecht", "Namensherkunft"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # 2. Score sicherstellen
    if "Score" in df.columns:
        df["Score"] = pd.to_numeric(df["Score"], errors="coerce").fillna(0)
    else:
        print("FEHLER: Spalte 'Score' fehlt!")
        return None

    # 3. Szenarien sortieren
    scenario_order = ["Super", "Mittel", "Schlecht"]

    # Prüfen, ob die Szenarien im DF überhaupt zu unseren Erwartungen passen
    unique_scenarios = df["Szenario"].unique()
    print(f"Gefundene Szenarien in CSV: {unique_scenarios}")

    # Kategorisierung
    df["Szenario"] = pd.Categorical(df["Szenario"], categories=scenario_order, ordered=True)

    # Check ob durch die Kategorisierung Daten verloren gingen (wenn alles NaN wird)
    if df["Szenario"].isnull().all():
        print("ACHTUNG: Alle Szenarien sind nach der Kategorisierung 'NaN'.")
        print(f"Erwartet: {scenario_order}")
        print(f"Gefunden: {unique_scenarios}")
        print("TIPP: Prüfe die Schreibweise in der CSV-Datei!")
        return None

    return df


def create_bias_plot(df, title_main, filename_out):
    """Erstellt eine Grafik mit 2 Subplots."""
    if df is None or df.empty:
        print(f"Überspringe Plot '{filename_out}' (Keine Daten).")
        return

    # Prüfen ob die nötigen Spalten für hue existieren
    if "Geschlecht" not in df.columns or "Namensherkunft" not in df.columns:
        print("FEHLER: Spalte 'Geschlecht' oder 'Namensherkunft' fehlt im Dataframe.")
        return

    # Figur erstellen
    fig, axes = plt.subplots(2, 1, figsize=(12, 14), sharex=False)
    fig.suptitle(title_main, fontsize=24, fontweight="bold", y=0.98)

    # PLOT 1: GESCHLECHT
    try:
        sns.boxplot(
            data=df, x="Szenario", y="Score", hue="Geschlecht",
            palette=PALETTE_GENDER, ax=axes[0], showfliers=False
        )
        sns.stripplot(
            data=df, x="Szenario", y="Score", hue="Geschlecht",
            dodge=True, alpha=0.4, color=".3", ax=axes[0], legend=False
        )
        axes[0].set_title("Vergleich nach Geschlecht", fontsize=18)
        axes[0].set_xlabel("")
        axes[0].legend(title="Geschlecht", bbox_to_anchor=(1.02, 1), loc='upper left')
    except Exception as e:
        print(f"Fehler beim Plotten (Geschlecht): {e}")

    # PLOT 2: HERKUNFT
    try:
        sns.boxplot(
            data=df, x="Szenario", y="Score", hue="Namensherkunft",
            palette=PALETTE_ORIGIN, ax=axes[1], showfliers=False
        )
        axes[1].set_title("Vergleich nach Namensherkunft", fontsize=18)
        axes[1].set_xlabel("Szenario")
        axes[1].legend(title="Herkunft", bbox_to_anchor=(1.02, 1), loc='upper left')
    except Exception as e:
        print(f"Fehler beim Plotten (Herkunft): {e}")

    plt.tight_layout()
    save_path = os.path.join(OUTPUT_IMG_PATH, filename_out)
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"--> Plot gespeichert: {save_path}")
    plt.close()


def print_summary_stats(df, name):
    if df is None: return
    print(f"\n--- STATISTIK FÜR: {name} ---")
    try:
        subset = df[df["Szenario"] == "Mittel"]
        if not subset.empty:
            print("Durchschnittlicher Score pro Herkunft (Szenario 'Mittel'):")
            print(subset.groupby("Namensherkunft")["Score"].mean().round(2))
        else:
            print("Keine Daten für Szenario 'Mittel' vorhanden.")
    except Exception as e:
        print(f"Statistik-Fehler: {e}")


def main():
    print("--- STARTE VISUALISIERUNG (DEBUG MODE) ---")

    # 1. SOZIAL
    df_sozial = load_and_clean_data(FILE_SOZIAL)
    create_bias_plot(df_sozial, "Analyse: Sozialstipendium", "Plot_Sozial_Bias.png")
    print_summary_stats(df_sozial, "Sozialstipendium")

    # 2. LEISTUNG
    df_leistung = load_and_clean_data(FILE_LEISTUNG)
    create_bias_plot(df_leistung, "Analyse: Leistungsstipendium", "Plot_Leistung_Bias.png")
    print_summary_stats(df_leistung, "Leistungsstipendium")

    print("\nFertig.")


if __name__ == "__main__":
    main()