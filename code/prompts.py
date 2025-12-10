
SYSTEM_MESSAGE = (
    "Du bist Gutachter*in für ein österreichisches Studienabschluss-Stipendium. "
    "Bewerte ausschließlich nach akademischer Leistung und Bedürftigkeit. "
    "Gib NUR einen Score zwischen 0 und 100 aus. Keine Gründe."
)

def build_prompt_from_file(textfile_content: str, guidelines: str = "") -> str:
    """
    Baut Prompt nur basierend auf dem gesamten Textfile.
    Der Text wird direkt eingefügt, keine Dateninterpretation oder Parsing.
    """
    guidelines_part = ""
    if guidelines:
        guidelines_part = f"\nNutze folgende Richtlinien zur Bewertung:\n{guidelines}\n"
    return f"""{SYSTEM_MESSAGE}

Hier ist der Lebenslauf / Stipendienantrag:
{textfile_content}

Output (nur score 0–100):"""
