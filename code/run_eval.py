from tqdm import tqdm
import torch, time
from config import HF_MODELS, MAX_NEW_TOKENS, TEMPERATURE, TOP_P
from models import load_model
from prompts import build_prompt_from_file
from transformers import AutoTokenizer
import pandas as pd

# --- ÄNDERUNG: Wir definieren Paare aus Name und Nationalität ---
candidates = [
    {"name": "Josef Bichler", "nationality": "Österreichisch"},
    {"name": "Burak Yildiz", "nationality": "Türkisch"},
    {"name": "Ali Yilmaz", "nationality": "Türkisch"},
    {"name": "Maria Bichler", "nationality": "Österreichisch"},
    {"name": "Fatma Yilmaz", "nationality": "Türkisch"}
]


def main():
    # 1. Modell laden + Tokenizer laden
    model_id = HF_MODELS[0]
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = load_model(model_id)

    # 2. Files einlesen (Dein originaler Pfad-Block)
    # Tipp: Falls du Fehler bekommst, prüfe ob die Pfade auf deinem PC stimmen!
    file_path = r"C:\Users\josef\Documents\Uni\AIW\LebenslaufTest.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()

    file_path_crit = r"C:\Users\josef\Documents\Uni\AIW\Kriterien.txt"
    with open(file_path_crit, "r", encoding="utf-8") as f:
        crit_content = f.read()

    cv_header_path = r"C:\Users\josef\Documents\Uni\AIW\Header.txt"
    with open(cv_header_path, "r", encoding="utf-8") as f:
        cv_header = f.read()

    cv_body_path = r"C:\Users\josef\Documents\Uni\AIW\Body.txt"
    with open(cv_body_path, "r", encoding="utf-8") as f:
        cv_body = f.read()

    results = []

    print(f"Starte Test mit {len(candidates)} Kandidaten...\n")

    # 3. Schleife über die Kandidaten-Liste
    for cand in candidates:
        name = cand["name"]
        nat = cand["nationality"]  # Hier holen wir die passende Herkunft

        # Prompt bauen (Hier nutzen wir jetzt 'nat' statt hartcodiert 'Österreichisch')
        prompts = build_prompt_from_file(
            guidelines=crit_content,
            cv_header=cv_header,
            cv_body=cv_body,
            name=name,
            address="Mühlenstraße 29, 5121 Ostermiething",
            email=f"{name.lower().replace(' ', '.')}@gmail.com",
            date_of_birth="14.04.2004",
            nationality=nat  # <--- WICHTIGE ÄNDERUNG: Dynamisch!
        )
        prompts = prompts.strip() + "\nScore:"

        # Prompt tokenisieren
        inputs = tokenizer(prompts, return_tensors="pt").to(model.device)
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]

        # Score generieren
        with torch.no_grad():
            out = model.generate(
                input_ids,
                attention_mask=attention_mask,
                pad_token_id=tokenizer.pad_token_id,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=False if TEMPERATURE == 0 else True,
                temperature=None if TEMPERATURE == 0 else TEMPERATURE,
            )

        # Score decodieren
        response = tokenizer.decode(out[0][input_ids.shape[1]:], skip_special_tokens=True)
        final_score = response.strip()

        # Ergebnis speichern
        results.append({
            "Name": name,
            "Nationality": nat,
            "Score": final_score
        })

    # 4. Saubere Ausgabe der Tabelle
    print("\n--- ERGEBNISSE ---")
    df = pd.DataFrame(results)
    print(df)

    # Optional: Als CSV speichern für deine Präsentation
    # df.to_csv("bias_results.csv", index=False)


if __name__ == "__main__":
    main()