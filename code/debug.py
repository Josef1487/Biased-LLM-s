import torch
from transformers import AutoTokenizer
from config import HF_MODELS, MAX_NEW_TOKENS
from models import load_model
from prompts import build_prompt_from_file
import os


def main():
    # 1. Setup
    model_id = HF_MODELS[0]
    base_path = r"C:\Users\josef\Documents\Uni\AIW"

    # Lade notwendige Dateien
    with open(os.path.join(base_path, "Kriterien.txt"), "r", encoding="utf-8") as f: crit = f.read()
    with open(os.path.join(base_path, "Header.txt"), "r", encoding="utf-8") as f: header = f.read()
    with open(os.path.join(base_path, "Body_borderline.txt"), "r", encoding="utf-8") as f: body = f.read()

    # 2. Modell
    print(f"Lade Modell {model_id}...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
    model = load_model(model_id)

    # 3. Prompt bauen
    prompt = build_prompt_from_file(
        guidelines=crit,
        cv_header=header,
        cv_body=body,
        name="Josef Bichler",
        address="Musterstraße 1",
        email="josef@test.com",
        date_of_birth="01.01.2000",
        nationality="Österreichisch"
    )
    prompt = prompt.strip()

    # 4. Inferenz
    print("\n--- Sende Prompt an Modell... ---")
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        out = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            pad_token_id=tokenizer.pad_token_id,
            max_new_tokens=200,  # Wir gönnen uns mehr Tokens zum Lesen
            do_sample=False
        )

    response = tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)

    print("\n--- ROH-ANTWORT VOM MODELL ---")
    print(response)
    print("------------------------------")


if __name__ == "__main__":
    main()