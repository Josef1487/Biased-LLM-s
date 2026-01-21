import os
# Builder importieren
from prompts import build_prompt_from_file as build_prompt_sozial
from prompt_leistung import build_prompt_from_file as build_prompt_leistung

# Config
BASE_PATH = r"C:\Development\Development PY\LLM\Biased-LLM-s"
OUTPUT_FILE = "DEBUG_ALL_PROMPTS.txt"

# Test-Dummy
CANDIDATE = {
    "Name": "Max Mustermann",
    "Geschlecht": "Männlich",
    "Nationalität": "Deutsch",
    "Wohnort": "Berlin",
    "Email": "max.mustermann@gmail.com",
    "Geburtsdatum": "14.04.2004"
}


# Datei-Reader Helper
def read_file(filename):
    path = os.path.join(BASE_PATH, filename)
    if not os.path.exists(path):
        return f"[FEHLER: Datei nicht gefunden: {path}]"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def main():
    print(f"--- ERSTELLE DEBUG-DATEI: {OUTPUT_FILE} ---")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:

        # ---------------------------------------------------------
        # Teil 1: Sozialstipendium
        # ---------------------------------------------------------
        out_f.write("=" * 60 + "\n")
        out_f.write("   TEIL 1: SOZIAL STIPENDIUM\n")
        out_f.write("=" * 60 + "\n\n")

        # Texte laden
        kriterien = read_file("Kriterien.txt")
        header = read_file("Header_sozial.txt")

        scenarios_sozial = {
            "SUPER": "Body_sozial_super.txt",
            "MITTEL": "Body_sozial_mittel.txt",
            "SCHLECHT": "Body_sozial_schlecht.txt"
        }

        for level, filename in scenarios_sozial.items():
            body_text = read_file(filename)

            # Prompt erstellen
            prompt = build_prompt_sozial(
                guidelines=kriterien,
                cv_header=header,
                cv_body=body_text,
                name=CANDIDATE["Name"],
                gender=CANDIDATE["Geschlecht"],
                address=CANDIDATE["Wohnort"],
                email=CANDIDATE["Email"],
                date_of_birth=CANDIDATE["Geburtsdatum"],
                nationality=CANDIDATE["Nationalität"]
            )

            # In Datei schreiben
            out_f.write(f"\n--- SZENARIO: {level} ({filename}) ---\n")
            out_f.write("-" * 40 + "\n")
            out_f.write(prompt)
            out_f.write("\n\n" + "#" * 60 + "\n\n")

        # ---------------------------------------------------------
        # Teil 2: Leistungsstipendium
        # ---------------------------------------------------------
        out_f.write("=" * 60 + "\n")
        out_f.write("   TEIL 2: LEISTUNGS STIPENDIUM\n")
        out_f.write("=" * 60 + "\n\n")

        # Texte laden
        kriterien_leistung = read_file("Kriterien_Leistung.txt")
        header = read_file("Header_sozial.txt") # Header recyceln
        base_body_leistung = read_file("Body_Leistung.txt")

        scenarios_leistung = {
            "SUPER": "Studienerfolg_super.txt",
            "MITTEL": "Studienerfolg_mittel.txt",
            "SCHLECHT": "Studienerfolg_schlecht.txt"
        }

        for level, filename in scenarios_leistung.items():
            erfolg_text = read_file(filename)

            # Prompt bauen (Body + Noten)
            prompt = build_prompt_leistung(
                guidelines=kriterien_leistung,
                cv_header=header,
                cv_body=base_body_leistung,
                cv_body2=erfolg_text,
                name=CANDIDATE["Name"],
                gender=CANDIDATE["Geschlecht"],
                address=CANDIDATE["Wohnort"],
                email=CANDIDATE["Email"],
                date_of_birth=CANDIDATE["Geburtsdatum"],
                nationality=CANDIDATE["Nationalität"]
            )

            # In Datei schreiben
            out_f.write(f"\n--- SZENARIO: {level} ({filename}) ---\n")
            out_f.write("-" * 40 + "\n")
            out_f.write(prompt)
            out_f.write("\n\n" + "#" * 60 + "\n\n")

    print(f"Fertig! Öffne die Datei '{OUTPUT_FILE}' um die Prompts zu prüfen.")


if __name__ == "__main__":
    main()