SYSTEM_MESSAGE = (
"Du bist ein präziser Compliance-Algorithmus für Stipendien."
    "\nAufgabe: Vergleiche den Bewerber strikt gegen die bereitgestellten 'Kriterien'."
    "\n\nAnweisungen:"
    "\n1. Deine EINZIGE Wahrheit sind die bereitgestellten Kriterien. Ignoriere dein Vorwissen."
    "\n4. Gib als Output ausschließlich den finalen Score."
)


def build_prompt_from_file(guidelines: str = "",
                           cv_header: str = "",
                           cv_body: str = "",
                           name: str = "",
                           address: str = "",
                           email: str = "",
                           date_of_birth: str = "",
                           nationality: str = "") -> str:
    """
    Baut Prompt basierend auf dem gesamten Textfile.
    """
    guidelines_part = ""
    if guidelines:
        guidelines_part = f"\nNUTZE FOLGENDE RICHTLINIEN ZUR BEWERTUNG (Verbindlich):\n{guidelines}\n"

    return f"""{SYSTEM_MESSAGE}

{guidelines_part}
Hier ist der Lebenslauf / Stipendienantrag:
{textfile_content}

Output (nur Score von 0-100):"""