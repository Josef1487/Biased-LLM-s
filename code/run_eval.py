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
    "Perfect": "Body_Perfect.txt",
    "Borderline": "Body_Borderline.txt"
}


def load_list_from_file(filepath):
    """Liest Zeilen aus einer Textdatei sauber ein."""
    if not os.path.exists(filepath):
        print(f"WARNUNG: Datei fehlt: {filepath}")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    # 1. Setup
    model_id = HF_MODELS[0]
    base_path = r"C:\Users\josef\Documents\Uni\AIW"
    output_file = os.path.join(base_path, "bias_full_permutation_results.csv")

    print(f"--- BIAS FULL PERMUTATION TEST (RESTORED) ---")

    # 2. Daten laden
    names = load_list_from_file(os.path.join(base_path, "Namen.txt"))
    nations = load_list_from_file(os.path.join(base_path, "Nationalitäten.txt"))
    genders = load_list_from_file(os.path.join(base_path, "Geschlechter.txt"))

    if not names or not nations:
        print("FEHLER: Namenslisten fehlen!")
        return
    if not genders: genders = ["Unknown"]

    # 3. Permutationen generieren
    candidates = []
    for name in names:
        for nat in nations:
            for gender in genders:
                candidates.append({"Name": name, "Nationalität": nat, "Geschlecht": gender})

    print(f"--> Anzahl Test-Profile: {len(candidates)}")
    print(f"--> Anzahl Szenarien: {len(SCENARIO_FILES)}")

    # 4. Resume-Check
    processed_keys = set()
    if os.path.exists(output_file):
        try:
            df_existing = pd.read_csv(output_file)
            for _, row in df_existing.iterrows():
                key = (row["Szenario"], row["Name"], row["Nationalität"], row["Geschlecht"])
                processed_keys.add(key)
        except:
            pass

    # 5. Modell laden
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_model(model_id)

    # Text-Bausteine laden
    try:
        with open(os.path.join(base_path, "Kriterien.txt"), "r", encoding="utf-8") as f:
            crit = f.read()
        with open(os.path.join(base_path, "Header.txt"), "r", encoding="utf-8") as f:
            head = f.read()
    except:
        return

    # 6. Loop
    for scenario_name, filename in SCENARIO_FILES.items():
        body_path = os.path.join(base_path, filename)
        if not os.path.exists(body_path): continue
        with open(body_path, "r", encoding="utf-8") as f:
            current_body = f.read()

        for cand in tqdm(candidates, desc=f"Szenario '{scenario_name}'"):
            name = cand["Name"]
            nat = cand["Nationalität"]
            gender = cand["Geschlecht"]

            if (scenario_name, name, nat, gender) in processed_keys: continue

            # Normaler String-Prompt (KEIN Chat-Template)
            prompts = build_prompt_from_file(
                guidelines=crit, cv_header=head, cv_body=current_body,
                name=name, address="Musterstraße 1", email="test@test.com",
                date_of_birth="01.01.2000", nationality=nat
            )

            inputs = tokenizer(prompts, return_tensors="pt").to(model.device)
            with torch.no_grad():
                out = model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    pad_token_id=tokenizer.pad_token_id,
                    max_new_tokens=MAX_NEW_TOKENS,
                    do_sample=False
                )

            response = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

            # --- BACK TO BASICS REGEX ---
           
            numbers = re.findall(r'\d+', response)
            if numbers:
                final_score = numbers[-1]
            else:
                final_score = "0"

            new_row = {"Szenario": scenario_name, "Name": name, "Nationalität": nat, "Geschlecht": gender,
                       "Score": final_score}

            df_new = pd.DataFrame([new_row])
            write_header = not os.path.exists(output_file)
            df_new.to_csv(output_file, mode='a', header=write_header, index=False)
            processed_keys.add((scenario_name, name, nat, gender))

    print(f"\nErgebnisse gespeichert in: {output_file}")


if __name__ == "__main__":
    main()