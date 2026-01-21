import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from tqdm import tqdm
from transformers import AutoTokenizer

# Importiere deine Module
from config import HF_MODELS, MAX_NEW_TOKENS, TEMPERATURE
from models import load_model
from prompts import build_prompt_from_file

# --- EINSTELLUNGEN ---
BATCH_SIZE = 16


def load_names_from_file(filepath, group_name):
    """Liest Namen Zeile für Zeile aus einer Textdatei"""
    names_list = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            # Jede Zeile lesen und Leerzeichen entfernen
            lines = [line.strip() for line in f if line.strip()]

        for name in lines:
            names_list.append({"Name": name, "Group": group_name})

        print(f"[Info] {len(lines)} Namen für '{group_name}' geladen.")
        return names_list
    except FileNotFoundError:
        print(f"[FEHLER] Datei nicht gefunden: {filepath}")
        return []


def extract_score(text):
    match = re.search(r'\d+', text)
    if match:
        return int(match.group())
    return 0


def plot_results(df, folder):
    try:
        plt.figure(figsize=(10, 6))
        sns.set_theme(style="whitegrid")

        # Plot erstellen
        ax = sns.boxplot(x="Group", y="Score", data=df, palette="Set2", showmeans=True)
        sns.stripplot(x="Group", y="Score", data=df, color=".3", size=4, alpha=0.6)

        plt.title(f"Bias-Analyse: {len(df)} Bewerbungen getestet", fontsize=16)
        plt.ylabel("Score (0-100)", fontsize=12)
        plt.xlabel("Gruppe", fontsize=12)
        plt.ylim(0, 105)

        plot_path = os.path.join(folder, "bias_plot.png")
        plt.savefig(plot_path)
        print(f"[Grafik] Gespeichert unter: {plot_path}")
    except Exception as e:
        print(f"Fehler beim Plotten: {e}")


def main():
    # 1. Setup & Pfade
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_folder = os.path.dirname(current_dir)
    print(f"[Setup] Projektordner: {project_folder}")

    # 2. Modell laden
    model_id = HF_MODELS[0]
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"
    model = load_model(model_id)

    # 3. Dateien lesen (Body, Header, Kriterien)
    try:
        with open(os.path.join(project_folder, "Kriterien.txt"), "r", encoding="utf-8") as f:
            crit_content = f.read()
        with open(os.path.join(project_folder, "Header.txt"), "r", encoding="utf-8") as f:
            cv_header = f.read()
        with open(os.path.join(project_folder, "Body.txt"), "r", encoding="utf-8") as f:
            cv_body = f.read()
    except FileNotFoundError as e:
        print(f"FEHLER: Basis-Dateien (Body/Header/Kriterien) nicht gefunden! {e}")
        return

    # 4. NAMEN AUS DATEIEN LADEN
    path_at = os.path.join(project_folder, "names_at.txt")
    path_tr = os.path.join(project_folder, "names_tr.txt")

    test_cases = []
    # Hier werden die 100 Namen pro Datei geladen
    test_cases += load_names_from_file(path_at, "Österreichisch")
    test_cases += load_names_from_file(path_tr, "Türkisch")

    if len(test_cases) == 0:
        print("[ABBRUCH] Keine Namen gefunden. Bitte names_at.txt und names_tr.txt erstellen!")
        return

    print(f"[Start] Teste insgesamt {len(test_cases)} Varianten in Paketen von {BATCH_SIZE}...")

    results = []

    # 5. LOOP (BATCH PROCESSING)
    for i in tqdm(range(0, len(test_cases), BATCH_SIZE), desc="KI bewertet..."):

        batch_items = test_cases[i: i + BATCH_SIZE]
        batch_prompts = []

        for item in batch_items:
            name = item["Name"]
            email_gen = f"{name.lower().replace(' ', '.')}@gmail.com"

            # WICHTIG: Hier wird das 'nationality' Feld leer gelassen (""),
            # damit die KI allein aufgrund des Namens urteilen muss.
            # Wenn du das "Schutzschild" wieder willst, schreib nationality="Österreichisch" rein.
            prompt = build_prompt_from_file(
                guidelines=crit_content,
                cv_header=cv_header,
                cv_body=cv_body,
                name=name,
                address="Mühlenstraße 29, 5121 Ostermiething",
                email=email_gen,
                date_of_birth="14.04.2004",
                nationality=""
            )
            batch_prompts.append(prompt.strip() + "\nScore:")

        # Tokenisieren & GPU
        inputs = tokenizer(batch_prompts, return_tensors="pt", padding=True).to(model.device)

        # Generieren
        with torch.no_grad():
            out = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                pad_token_id=tokenizer.pad_token_id,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False if TEMPERATURE == 0 else True,
                temperature=None if TEMPERATURE == 0 else TEMPERATURE,
            )

        # Decodieren
        input_len = inputs["input_ids"].shape[1]
        generated_tokens = out[:, input_len:]
        decoded_responses = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

        # Speichern
        for item, response in zip(batch_items, decoded_responses):
            score = extract_score(response)
            results.append({
                "Name": item["Name"],
                "Group": item["Group"],
                "Score": score,
                "Raw Answer": response.strip()
            })

    # 6. ABSCHLUSS & STATISTIK
    df = pd.DataFrame(results)

    csv_path = os.path.join(project_folder, "results_bias.csv")
    df.to_csv(csv_path, index=False)
    print(f"[Fertig] Daten gespeichert: {csv_path}")

    print("\n" + "=" * 50)
    print("   ERGEBNIS-ZUSAMMENFASSUNG (DURCHSCHNITT)")
    print("=" * 50)

    summary = df.groupby("Group")["Score"].mean().round(2)
    print(summary)

    print("-" * 50)
    try:
        diff = summary["Österreichisch"] - summary["Türkisch"]
        if diff > 0:
            print(f"--> Bias erkannt: Österreichische Namen haben {diff:.2f} Punkte MEHR.")
        elif diff < 0:
            print(f"--> Bias erkannt: Türkische Namen haben {abs(diff):.2f} Punkte MEHR.")
        else:
            print("--> Kein Bias: Exakt gleicher Durchschnitt.")
    except:
        pass

    print("=" * 50 + "\n")

    plot_results(df, project_folder)


if __name__ == "__main__":
    main()