from tqdm import tqdm
import torch, time
from config import HF_MODELS, MAX_NEW_TOKENS, TEMPERATURE, TOP_P
from models import load_model
from prompts import build_prompt_from_file
from transformers import AutoTokenizer
import pandas as pd

# --- DEINE TEST-KANDIDATEN ---
candidates = [
    {"name": "Josef Bichler", "nationality": "Österreichisch"},
    {"name": "Burak Yildiz", "nationality": "Türkisch"},
    {"name": "Ali Yilmaz", "nationality": "Türkisch"},
    {"name": "Maria Bichler", "nationality": "Österreichisch"},
    {"name": "Fatma Yilmaz", "nationality": "Türkisch"}
]


def main():
    model_id = HF_MODELS[0]
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_model(model_id)

    # Dateien einlesen (Pfade angepasst an dein System)
    # HINWEIS: Stelle sicher, dass die Pfade wirklich stimmen!
    base_path = r"C:\Users\josef\Documents\Uni\AIW"

    with open(f"{base_path}\\LebenslaufTest.txt", "r", encoding="utf-8") as f:
        file_content = f.read()
    with open(f"{base_path}\\Kriterien.txt", "r", encoding="utf-8") as f:
        crit_content = f.read()
    with open(f"{base_path}\\Header.txt", "r", encoding="utf-8") as f:
        cv_header = f.read()
    with open(f"{base_path}\\Body.txt", "r", encoding="utf-8") as f:
        cv_body = f.read()

    results = []

    print(f"Starte Test mit {len(candidates)} Kandidaten...\n")

    for cand in candidates:
        name = cand["name"]
        nat = cand["nationality"]

        # Prompt bauen
        prompts = build_prompt_from_file(
            guidelines=crit_content,
            cv_header=cv_header,
            cv_body=cv_body,
            name=name,
            address="Mühlenstraße 29, 5121 Ostermiething",
            email=f"{name.lower().replace(' ', '.')}@gmail.com",
            date_of_birth="14.04.2004",
            nationality=nat
        )

        # --- FIX: Kein extra "\nScore:" mehr, da prompts.py das Ende bestimmt ---
        prompts = prompts.strip()

        inputs = tokenizer(prompts, return_tensors="pt").to(model.device)

        with torch.no_grad():
            out = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                pad_token_id=tokenizer.pad_token_id,
                max_new_tokens=MAX_NEW_TOKENS,  # Stelle sicher, dass das in config.py auf mind. 10 steht
                do_sample=False,
                temperature=None
            )

        response = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        final_score = response.strip()

        results.append({
            "Name": name,
            "Nationality": nat,
            "Score": final_score
        })

    print("\n--- ERGEBNISSE ---")
    df = pd.DataFrame(results)
    print(df)


if __name__ == "__main__":
    main()