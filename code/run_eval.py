from tqdm import tqdm
import torch, time
from config import HF_MODELS, MAX_NEW_TOKENS, TEMPERATURE, TOP_P
from models import load_model
from prompts import build_prompt_from_file
from transformers import AutoTokenizer

def main():
    # 1. Modell laden + Tokenizer laden
    model_id = HF_MODELS[0]
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = load_model(model_id)

    # 2. Lebenslauf-File einlesen
    file_path = r"C:\Users\josef\Documents\Uni\AIW\LebenslaufDemo_JosefBichler.txt"
    with open(file_path, "r", encoding="utf-8") as f:
        file_content = f.read()
    file_path_crit = r"C:\Users\josef\Documents\Uni\AIW\Kriterien.txt"
    with open(file_path_crit, "r", encoding="utf-8") as f:
        crit_content = f.read()

    # 3. Prompt bauen
    prompts = build_prompt_from_file(file_content, crit_content)
    prompts = prompts.strip() + "\nScore:"

    # 4. Prompt tokenisieren
    inputs = tokenizer(prompts, return_tensors="pt").to(model.device)
    input_ids = inputs["input_ids"]

    # 5. Fortschrittsbalken anzeigen (GPU-Loading + Inference kleiner Deko-Balken)
    for _ in tqdm(range(100), desc="Progress", bar_format="{percentage:3.0f}%|{bar}|{r_bar}"):
        time.sleep(0.002)  # extrem kurzer sleep -> blockiert fast nix

    # 6. Score generieren
    with torch.no_grad():
        out = model.generate(
            input_ids,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False if TEMPERATURE == 0 else True,
            temperature=None if TEMPERATURE == 0 else TEMPERATURE,
        )

    # 7. Score decodieren
    response = tokenizer.decode(out[0][input_ids.shape[1]:], skip_special_tokens=True)
    print(f"Final score: {response.strip()}")

if __name__ == "__main__":
    main()
