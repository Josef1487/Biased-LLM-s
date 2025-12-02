
# Hugging Face Modell-IDs (du kannst hier tauschen/erweitern)
HF_MODELS = [
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",        # klein, läuft ohne GPU
    # "meta-llama/Meta-Llama-3-8B-Instruct",     # stärker, braucht GPU & HF-Zugang
    # "mistralai/Mistral-7B-Instruct-v0.2",      # gute Option mit GPU
]

# Generation Settings
MAX_NEW_TOKENS = 4
TEMPERATURE = 0.1          # 0 = deterministischer, besser für Vergleich
TOP_P = 0.9


