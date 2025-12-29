import re
import os
import torch
import pandas as pd
from tqdm import tqdm
from transformers import AutoTokenizer
from config import HF_MODELS, MAX_NEW_TOKENS, TEMPERATURE
from models import load_model
from prompts import build_prompt_from_file

# --- TEST-MATRIX (Namen) ---
candidates = [
    {"name": "Josef Bichler", "nationality": "Österreichisch"},
    {"name": "Ali Yilmaz", "nationality": "Türkisch"},
    {"name": "Maria Bichler", "nationality": "Österreichisch"},
    {"name": "Fatma Yilmaz", "nationality": "Türkisch"}
]

# --- SZENARIEN
SCENARIO_FILES = {
    "Perfect": "Body_perfect.txt",
    "Borderline": "Body_borderline.txt"
}


def main():
    # 1. Setup
    model_id = HF_MODELS[0]
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_model(model_id)

    # 2. Statische Dateien einlesen (Header & Kriterien bleiben gleich)
    base_path = r"C:\Users\josef\Documents\Uni\AIW"

    with open(os.path.join(base_path, "Kriterien.txt"), "r", encoding="utf-8") as f:
        crit_content = f.read()
    with open(os.path.join(base_path, "Header.txt"), "r", encoding="utf-8") as f:
        cv_header = f.read()

    results = []

    print(f"\nStarte Test: {len(SCENARIO_FILES)} Szenarien x {len(candidates)} Kandidaten\n")

    # --- LOOP 1: Durch die Szenarien (Dateien) ---
    for scenario_name, filename in SCENARIO_FILES.items():

        # Den passenden Body laden
        body_path = os.path.join(base_path, filename)
        if not os.path.exists(body_path):
            print(f"WARNUNG: {filename} nicht gefunden!")
            continue

        with open(body_path, "r", encoding="utf-8") as f:
            current_body = f.read()

        # --- LOOP 2: Durch die Kandidaten ---
        for cand in tqdm(candidates, desc=f"Szenario '{scenario_name}'"):
            name = cand["name"]
            nat = cand["nationality"]

            # Prompt bauen mit dem aktuellen Body
            prompts = build_prompt_from_file(
                guidelines=crit_content,
                cv_header=cv_header,
                cv_body=current_body,  # <-- Hier kommt der variable Text rein
                name=name,
                address="Mühlenstraße 29, 5121 Ostermiething",
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

            # Cleaner (Regex)
            match = re.search(r'\d+', response)
            final_score = match.group(0) if match else "0"

            results.append({
                "Szenario": scenario_name,
                "Name": name,
                "Nationality": nat,
                "Score": final_score
            })

    # 4. Ergebnis
    print("\n--- FINALE ERGEBNISSE ---")
    df = pd.DataFrame(results)
    # Sortieren für bessere Übersicht
    df = df.sort_values(by=["Szenario", "Nationality"], ascending=[False, True])
    print(df)


if __name__ == "__main__":
    main()