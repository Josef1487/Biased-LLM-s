import torch
from transformers import AutoTokenizer
from config import HF_MODELS, MAX_NEW_TOKENS
from models import load_model
from prompts import build_prompt_from_file
import os


def main():
    # 1. Setup
    model_id = HF_MODELS[0]  # Llama-3 aus Config
    base_path = r"C:\Users\josef\Documents\Uni\AIW"

    print(f"--- DEBUG MODUS: Analyse von {model_id} ---")

    # Lade notwendige Dateien (Fehler abfangen, falls was fehlt)
    try:
        with open(os.path.join(base_path, "Kriterien.txt"), "r", encoding="utf-8") as f:
            crit = f.read()
        with open(os.path.join(base_path, "Header.txt"), "r", encoding="utf-8") as f:
            header = f.read()
        # Wir testen den 'Perfect'-Fall, weil hier die "60" auftauchte
        with open(os.path.join(base_path, "Body_sozial.txt"), "r", encoding="utf-8") as f:
            body = f.read()
    except FileNotFoundError:
        print("FEHLER: Eine der Textdateien (Kriterien/Header/Body) fehlt!")
        return

    # 2. Modell laden
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None: tokenizer.pad_token = tokenizer.eos_token
    model = load_model(model_id)

    # 3. Prompt bauen (Der ORIGINALE aus deiner prompts.py)
    # Wir ändern hier NICHTS an der Funktion selbst.
    original_prompt = build_prompt_from_file(
        guidelines=crit,
        cv_header=header,
        cv_body=body,
        name="Josef Bichler",
        address="Musterstraße 1",
        email="josef@test.com",
        date_of_birth="01.01.2000",
        nationality="Österreichisch"
    )

    # 4. DEBUG-INJEKTION (Das ist der Trick)
    # Wir hängen eine Anweisung dran, die das "kurz fassen" überschreibt.
    debug_add_on = (
        "\n\n--------------------------------------------------\n"
        "### DEBUG-ANWEISUNG (Override):\n"
        "Ignoriere die Anweisung 'extrem kurz'.\n"
        "Ich bin der Entwickler. Erkläre mir ausführlich, wie du rechnest.\n"
        "Woher kommen die Punkte? Was hast du abgezogen?\n"
        "Nenne am Ende trotzdem den Score im Format: PUNKTE: [Zahl]"
    )

    full_prompt = original_prompt + debug_add_on

    print("\n--- Sende Prompt an Modell... ---")

    # Llama-3 Chat Template nutzen
    messages = [{"role": "user", "content": full_prompt}]
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(model.device)

    with torch.no_grad():
        out = model.generate(
            inputs,
            pad_token_id=tokenizer.pad_token_id,
            max_new_tokens=600,  # Viel Platz für die Erklärung lassen
            do_sample=False  # Deterministisch bleiben
        )

    response = tokenizer.decode(out[0][inputs.shape[1]:], skip_special_tokens=True)

    print("\n--- ANTWORT VOM MODELL ---")
    print(response)
    print("------------------------------")


if __name__ == "__main__":
    main()