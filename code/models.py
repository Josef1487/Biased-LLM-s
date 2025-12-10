from transformers import AutoModelForCausalLM
import torch

MODEL_CACHE = {}

def load_model(model_id: str):
    """
    Lädt ein Modell von Hugging Face lokal.
    Nutzt Cache, damit es nur 1× geladen wird.
    """
    if model_id in MODEL_CACHE:
        print("[models] Modell aus Cache geladen.")
        return MODEL_CACHE[model_id]

    print(f"[models] Lade Modell: {model_id}")
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    )
    model.eval()

    MODEL_CACHE[model_id] = model
    return model