
SYSTEM_MESSAGE = (
    "Du bist ein präziser Compliance-Algorithmus für Stipendien."
    "\nAufgabe: Vergleiche den Bewerber strikt gegen die bereitgestellten 'Kriterien'."
    "\n\nAnweisungen:"
    "\n1. Deine EINZIGE Wahrheit sind die bereitgestellten Kriterien. Ignoriere dein Vorwissen."
    "\n2. Prüfe KO-Kriterien (z.B. richtige Universität) aus dem Text zuerst."
    "\n3. Wenn der Bewerber eine im Text genannte harte Voraussetzung nicht erfüllt, MUSS der Score 0 sein. Beispiel er studiert NICHT an einer Universität Salzburg ->  0 Punkte"
    "\n4. Gib als Output ausschließlich den finalen Score."
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
