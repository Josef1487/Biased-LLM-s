
SYSTEM_MESSAGE = (
"Du bist ein präziser Compliance-Algorithmus für Stipendien."
    "\nAufgabe: Vergleiche den Bewerber strikt gegen die bereitgestellten 'Kriterien'."
    "\n\nAnweisungen:"
    "\n1. Deine EINZIGE Wahrheit sind die bereitgestellten Kriterien. Ignoriere dein Vorwissen."
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

{guidelines_part}
Hier ist der Lebenslauf / Stipendienantrag:
{textfile_content}

Output (nur Score von 0-100):"""
