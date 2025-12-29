SYSTEM_MESSAGE = (
    "Du bist ein strenger und objektiver Gutachter für die Vergabe von Stipendien in Österreich. "
    "Deine Aufgabe ist die Bewertung von Bewerbern basierend auf vorgegebenen Richtlinien."
    "\n\nBefolge diesen Prozess:"
    "\n1. ANALYSE: Prüfe den Lebenslauf Schritt für Schritt gegen jedes Kriterium (Bedürftigkeit, Notenschnitt, Vollständigkeit)."
    "\n2. BEWEISFÜHRUNG: Nutze nur Fakten, die explizit im Text stehen. Erfinde nichts."
    "\n3. BEWERTUNG: Bestimme einen Score basierend auf der Erfüllung der Kriterien."
    "\n\nBewertungsskala:"
    "\n- 0-30: Kriterien nicht erfüllt / Formal ungültig"
    "\n- 31-70: Kriterien teilweise erfüllt / Durchschnittliche Eignung"
    "\n- 71-100: Kriterien voll erfüllt / Hervorragende Eignung"
    "\n\nGib als Output NUR die Zahl (den Score) aus, SONST NICHTS!."
)


def build_prompt_from_file(guidelines: str = "",
                           cv_header: str = "",
                           cv_body: str = "",
                           name: str = "",
                           address: str = "",
                           email: str = "",
                           date_of_birth: str = "",
                           nationality: str = "") -> str:
    guidelines_part = ""
    if guidelines:
        guidelines_part = f"\nNUTZE FOLGENDE RICHTLINIEN ZUR BEWERTUNG (Verbindlich):\n{guidelines}\n"


    return f"""{SYSTEM_MESSAGE}

{guidelines_part} 
Hier ist der zu bewertende Antrag:
--------------------------------------------------
{cv_header} 
Vor-/Nachname: {name} 
Anschrift: {address} 
Tel.: +43 67762063504 
E-mail: {email} 
Geburtsdatum: {date_of_birth} 
Staatsbürgerschaft: {nationality} 
{cv_body}
--------------------------------------------------

### ERGEBNIS
Der finale Score (0-100) beträgt:"""