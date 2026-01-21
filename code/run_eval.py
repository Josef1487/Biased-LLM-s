import re
import os
import torch
import pandas as pd
from tqdm import tqdm
from transformers import AutoTokenizer
from config import HF_MODELS, MAX_NEW_TOKENS, TEMPERATURE
from models import load_model
from prompts import build_prompt_from_file


# --- KONFIGURATION ---
SCENARIO_FILES = {
    "Super": "Body_sozial_super.txt",
    "Mittel": "Body_sozial_mittel.txt",
    "Schlecht": "Body_sozial_schlecht.txt",
}


def load_list_from_file(filepath):
    """Liest Zeilen aus einer Textdatei sauber ein."""
    if not os.path.exists(filepath):
        print(f"WARNUNG: Datei fehlt: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        # Entfernt Leerzeichen und leere Zeilen
        return [line.strip() for line in f if line.strip()]


def main():
    # 1. Setup
    model_id = HF_MODELS[0]
    base_path = r"C:\Users\josef\Documents\Uni\AIW"
    output_file = os.path.join(base_path, "bias_full_permutation_results.csv")  # Neuer Dateiname

    print(f"--- BIAS FULL PERMUTATION TEST ---")

    # 2. Daten laden (Die 3 Listen)
    names_data = pd.read_csv(
        os.path.join(base_path, "Namen.txt"),
        header=None,
        names=["Name", "Origin"]
    ).to_dict(orient="records")

    nations = load_list_from_file(os.path.join(base_path, "Nationalitäten.txt"))
    genders = load_list_from_file(os.path.join(base_path, "Geschlechter.txt"))
    locations = load_list_from_file(os.path.join(base_path, "Wohnorte.txt"))

    if not names_data or not nations:
        print("FEHLER: 'names.txt' und 'nations.txt' dürfen nicht leer sein!")
        return

    # Falls genders.txt leer ist oder fehlt, setzen wir einen Default
    if not genders:
        genders = ["Unknown"]

    # 3. PERMUTATIONEN GENERIEREN (Die Matrix)
    candidates = []
    print(f"\nGeneriere ALLE Kombinationen aus:")
    print(f"- {len(names_data)} Namen")
    print(f"- {len(nations)} Nationalitäten")
    print(f"- {len(genders)} Geschlechtern")
    print(f"- {len(locations)} Wohnorte")

    # Der Loop erstellt jede mögliche Kombination
    for entry in names_data:
        name = entry["Name"]
        origin = entry["Origin"]
        for nat in nations:
            for gender in genders:
                for loc in locations:
                    cand_nat = "" if nat == "LEER" else nat
                    cand_gender = "" if gender == "LEER" else gender
                    cand_loc = "" if loc == "LEER" else loc

                    candidates.append({
                        "Name": name,
                        "Namensherkunft": origin,
                        "Nationalität": cand_nat,
                        "Geschlecht": cand_gender,
                        "Wohnort": cand_loc,
                    })

    print(f"--> Anzahl Test-Profile: {len(candidates)}")
    print(f"--> Anzahl Szenarien: {len(SCENARIO_FILES)}")
    print(f"--> GESAMT-DURCHLÄUFE: {len(candidates) * len(SCENARIO_FILES)}")


    # 4. Resume-Logik (Falls du abbrichst und neustartest)
    processed_keys = set()
    if os.path.exists(output_file):
        print("DEBUG: Datei gefunden! Versuche zu lesen...")
        try:
            df_existing = pd.read_csv(output_file).fillna("")
            for _, row in df_existing.iterrows():
                # Schlüssel: Szenario + Name + Nationalität + Geschlecht
                key = (row["Szenario"], row["Name"], row["Nationalität"], row["Geschlecht"], row["Wohnort"])
                processed_keys.add(key)
            print(f"--> Überspringe {len(processed_keys)} bereits erledigte Einträge.")
        except Exception as e:
            print(f"Fehler beim laden")
            print(f"Fehlermeldung: {e}")


    # 5. Modell laden
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_model(model_id)

    # Templates laden
    try:
        with open(os.path.join(base_path, "Kriterien.txt"), "r", encoding="utf-8") as f:
            crit_content = f.read()
        with open(os.path.join(base_path, "Header_sozial.txt"), "r", encoding="utf-8") as f:
            cv_header = f.read()
    except FileNotFoundError:
        print("FEHLER: Header.txt oder Kriterien.txt fehlt!")
        return

    # 6. DER HAUPT-LOOP
    for scenario_name, filename in SCENARIO_FILES.items():
        body_path = os.path.join(base_path, filename)
        if not os.path.exists(body_path): continue
        with open(body_path, "r", encoding="utf-8") as f:
            current_body = f.read()

        for cand in tqdm(candidates, desc=f"Szenario '{scenario_name}'"):
            name = cand["Name"]
            origin = cand["Namensherkunft"]
            nat = cand["Nationalität"]
            gender = cand["Geschlecht"]
            location = cand["Wohnort"]

            # Check ob schon erledigt
            if (scenario_name, name, nat, gender, location) in processed_keys:
                continue

            # Prompt bauen
            prompts = build_prompt_from_file(
                guidelines=crit_content,
                cv_header=cv_header,
                cv_body=current_body,
                name=name,
                gender=gender,
                address=location,
                email=f"{name.lower().replace(' ', '.')}@gmail.com",
                date_of_birth="14.04.2004",
                nationality=nat
            )
            prompts = prompts.strip()

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
            match = re.search(r'\d+', response)
            final_score = match.group(0) if match else "0"

            # Sofort speichern (Append)
            new_row = {
                "Szenario": scenario_name,
                "Name": name,
                "Namensherkunft": origin,
                "Nationalität": nat,
                "Geschlecht": gender,
                "Wohnort": location,
                "Score": final_score
            }

            df_new = pd.DataFrame([new_row])
            write_header = not os.path.exists(output_file)
            df_new.to_csv(output_file, mode='a', header=write_header, index=False)

            # Key merken damit wir ihn im selben Lauf nicht nochmal machen
            processed_keys.add((scenario_name, name, nat, gender, location))

    print(f"\n Alle Ergebnisse in: {output_file}")


if __name__ == "__main__":
    main()