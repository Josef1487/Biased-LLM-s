import re
import os
import torch
import pandas as pd
from tqdm import tqdm
from transformers import AutoTokenizer
from config import HF_MODELS, MAX_NEW_TOKENS, TEMPERATURE
from models import load_model

# WICHTIG: Wir importieren beide Prompt-Builder und benennen sie um, damit sie sich nicht beißen
from prompts import build_prompt_from_file as build_prompt_sozial
from prompt_leistung import build_prompt_from_file as build_prompt_leistung

# --- KONFIGURATION ALLGEMEIN ---
BASE_PATH = r"C:\Development\Development PY\LLM\Biased-LLM-s"
MODEL_ID = HF_MODELS[0]

# --- KONFIGURATION SOZIAL ---
SCENARIO_FILES_SOZIAL = {
    "Super": "Body_sozial_super.txt",
    "Mittel": "Body_sozial_mittel.txt",
    "Schlecht": "Body_sozial_schlecht.txt",
}
OUTPUT_FILE_SOZIAL = os.path.join(BASE_PATH, "bias_results_SOZIAL.csv")

# --- KONFIGURATION LEISTUNG ---
SCENARIO_FILES_LEISTUNG = {
    "Super": "Studienerfolg_super.txt",
    "Mittel": "Studienerfolg_mittel.txt",
    "Schlecht": "Studienerfolg_schlecht.txt",
}
OUTPUT_FILE_LEISTUNG = os.path.join(BASE_PATH, "bias_results_LEISTUNG.csv")


def load_list_from_file(filepath):
    """Liest Zeilen aus einer Textdatei sauber ein."""
    if not os.path.exists(filepath):
        print(f"WARNUNG: Datei fehlt: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def get_existing_keys(filepath):
    """Liest bereits bearbeitete Einträge aus der CSV, um Duplikate zu vermeiden."""
    processed_keys = set()
    if os.path.exists(filepath):
        try:
            df_existing = pd.read_csv(filepath).fillna("")
            for _, row in df_existing.iterrows():
                # Schlüssel: Szenario + Name + Nationalität + Geschlecht + Ort
                key = (row["Szenario"], row["Name"], row["Nationalität"], row["Geschlecht"], row["Wohnort"])
                processed_keys.add(key)
        except Exception as e:
            print(f"Fehler beim Lesen von {filepath}: {e}")
    return processed_keys


def extract_score(response_text):
    """Hilfsfunktion um die Zahl aus der Antwort zu holen."""
    match = re.search(r'\d+', response_text)
    return match.group(0) if match else "0"


# ---------------------------------------------------------
# FUNKTION 1: SOZIALSTIPENDIUM
# ---------------------------------------------------------
def evaluate_sozial(model, tokenizer, candidates, processed_keys):
    print(f"\n>>> STARTE EVALUIERUNG: SOZIALSTIPENDIUM")
    print(f"--> Ziel-Datei: {OUTPUT_FILE_SOZIAL}")

    # Templates laden
    try:
        with open(os.path.join(BASE_PATH, "Kriterien.txt"), "r", encoding="utf-8") as f:
            crit_content = f.read()
        with open(os.path.join(BASE_PATH, "Header_sozial.txt"), "r", encoding="utf-8") as f:
            cv_header = f.read()
    except FileNotFoundError:
        print("FEHLER (Sozial): Header.txt oder Kriterien.txt fehlt! Überspringe...")
        return

    for scenario_name, filename in SCENARIO_FILES_SOZIAL.items():
        body_path = os.path.join(BASE_PATH, filename)
        if not os.path.exists(body_path):
            print(f"Datei fehlt: {body_path}")
            continue

        with open(body_path, "r", encoding="utf-8") as f:
            current_body = f.read()

        for cand in tqdm(candidates, desc=f"Sozial - {scenario_name}"):
            # Check Resume
            key = (scenario_name, cand["Name"], cand["Nationalität"], cand["Geschlecht"], cand["Wohnort"])
            if key in processed_keys:
                continue

            # Prompt bauen (Nutzt die importierte Funktion für SOZIAL)
            prompts = build_prompt_sozial(
                guidelines=crit_content,
                cv_header=cv_header,
                cv_body=current_body,
                name=cand["Name"],
                gender=cand["Geschlecht"],
                address=cand["Wohnort"],
                email=f"{cand['Name'].lower().replace(' ', '.')}@gmail.com",
                date_of_birth="14.04.2004",
                nationality=cand["Nationalität"]
            ).strip()

            # Inferenz
            inputs = tokenizer(prompts, return_tensors="pt").to(model.device)
            with torch.no_grad():
                out = model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    pad_token_id=tokenizer.pad_token_id,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=False,
                    temperature=None
                )

            response = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            final_score = extract_score(response)

            # Speichern
            new_row = {
                "Szenario": scenario_name,
                "Name": cand["Name"],
                "Namensherkunft": cand["Namensherkunft"],
                "Nationalität": cand["Nationalität"],
                "Geschlecht": cand["Geschlecht"],
                "Wohnort": cand["Wohnort"],
                "Score": final_score
            }

            df_new = pd.DataFrame([new_row])
            write_header = not os.path.exists(OUTPUT_FILE_SOZIAL)
            df_new.to_csv(OUTPUT_FILE_SOZIAL, mode='a', header=write_header, index=False)

            # Key zur Laufzeitliste hinzufügen
            processed_keys.add(key)


# ---------------------------------------------------------
# FUNKTION 2: LEISTUNGSSTIPENDIUM
# ---------------------------------------------------------
def evaluate_leistung(model, tokenizer, candidates, processed_keys):
    print(f"\n>>> STARTE EVALUIERUNG: LEISTUNGSSTIPENDIUM")
    print(f"--> Ziel-Datei: {OUTPUT_FILE_LEISTUNG}")

    # Templates laden
    try:
        with open(os.path.join(BASE_PATH, "Kriterien_Leistung.txt"), "r", encoding="utf-8") as f:
            crit_content = f.read()
        with open(os.path.join(BASE_PATH, "Header_sozial.txt"), "r",
                  encoding="utf-8") as f:  # Nutzt scheinbar gleichen Header?
            cv_header = f.read()
        with open(os.path.join(BASE_PATH, "Body_Leistung.txt"), "r", encoding="utf-8") as f:
            base_body = f.read()
    except FileNotFoundError:
        print("FEHLER (Leistung): Kriterien_Leistung.txt, Header oder Body_Leistung fehlt!")
        return

    for scenario_name, filename in SCENARIO_FILES_LEISTUNG.items():
        erfolg_path = os.path.join(BASE_PATH, filename)
        if not os.path.exists(erfolg_path):
            print(f"Datei fehlt: {erfolg_path}")
            continue

        with open(erfolg_path, "r", encoding="utf-8") as f:
            erfolg_text = f.read()

        for cand in tqdm(candidates, desc=f"Leistung - {scenario_name}"):
            # Check Resume
            key = (scenario_name, cand["Name"], cand["Nationalität"], cand["Geschlecht"], cand["Wohnort"])
            if key in processed_keys:
                continue

            # Prompt bauen (Nutzt die importierte Funktion für LEISTUNG)
            # ACHTUNG: Hier werden cv_body UND cv_body2 übergeben
            prompts = build_prompt_leistung(
                guidelines=crit_content,
                cv_header=cv_header,
                cv_body=base_body,  # Der allgemeine Teil
                cv_body2=erfolg_text,  # Der spezifische Leistungsteil (Noten etc.)
                name=cand["Name"],
                gender=cand["Geschlecht"],
                address=cand["Wohnort"],
                email=f"{cand['Name'].lower().replace(' ', '.')}@gmail.com",
                date_of_birth="14.04.2004",
                nationality=cand["Nationalität"]
            ).strip()

            # Inferenz
            inputs = tokenizer(prompts, return_tensors="pt").to(model.device)
            with torch.no_grad():
                out = model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    pad_token_id=tokenizer.pad_token_id,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=False,
                    temperature=None
                )

            response = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
            final_score = extract_score(response)

            # Speichern
            new_row = {
                "Szenario": scenario_name,
                "Name": cand["Name"],
                "Namensherkunft": cand["Namensherkunft"],
                "Nationalität": cand["Nationalität"],
                "Geschlecht": cand["Geschlecht"],
                "Wohnort": cand["Wohnort"],
                "Score": final_score
            }

            df_new = pd.DataFrame([new_row])
            write_header = not os.path.exists(OUTPUT_FILE_LEISTUNG)
            df_new.to_csv(OUTPUT_FILE_LEISTUNG, mode='a', header=write_header, index=False)

            processed_keys.add(key)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def main():
    print(f"--- BIAS FULL PERMUTATION TEST (COMBINED) ---")

    # 1. Daten laden (Einmalig für alle Tests)
    names_path = os.path.join(BASE_PATH, "Namen.txt")
    if not os.path.exists(names_path):
        print(f"FEHLER: {names_path} nicht gefunden.")
        return

    names_data = pd.read_csv(names_path, header=None, names=["Name", "Origin"]).to_dict(orient="records")
    nations = load_list_from_file(os.path.join(BASE_PATH, "Nationalitäten.txt"))
    genders = load_list_from_file(os.path.join(BASE_PATH, "Geschlechter.txt")) or ["Unknown"]
    locations = load_list_from_file(os.path.join(BASE_PATH, "Wohnorte.txt"))

    # 2. Permutationen erstellen
    candidates = []
    print(f"\nGeneriere Kandidaten-Matrix...")
    for entry in names_data:
        for nat in nations:
            for gender in genders:
                for loc in locations:
                    candidates.append({
                        "Name": entry["Name"],
                        "Namensherkunft": entry["Origin"],
                        "Nationalität": "" if nat == "LEER" else nat,
                        "Geschlecht": "" if gender == "LEER" else gender,
                        "Wohnort": "" if loc == "LEER" else loc,
                    })

    print(f"--> Anzahl Kandidaten pro Szenario: {len(candidates)}")

    # 3. Modell laden (Nur einmal!)
    print(f"--> Lade Modell: {MODEL_ID}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_model(MODEL_ID)

    # 4. START TASK 1: SOZIAL
    # Wir laden erst die Keys der Sozial-CSV, falls wir dort weitermachen müssen
    keys_sozial = get_existing_keys(OUTPUT_FILE_SOZIAL)
    print(f"--> Bereits erledigte Sozial-Einträge: {len(keys_sozial)}")
    evaluate_sozial(model, tokenizer, candidates, keys_sozial)

    # 5. START TASK 2: LEISTUNG
    # Wir laden die Keys der Leistungs-CSV
    keys_leistung = get_existing_keys(OUTPUT_FILE_LEISTUNG)
    print(f"--> Bereits erledigte Leistungs-Einträge: {len(keys_leistung)}")
    evaluate_leistung(model, tokenizer, candidates, keys_leistung)

    print("\n--- ALLE TESTS ABGESCHLOSSEN ---")


if __name__ == "__main__":
    main()