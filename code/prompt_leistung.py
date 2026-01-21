SYSTEM_MESSAGE = (
    "Du bist ein objektiver Gutachter für Stipendien in Österreich. Deine Aufgabe: Prüfe, ob der Antrag die beigefügten RICHTLINIEN erfüllt und wie passend der Kandidat für das jeweilige Stipendium ist."
    "\n\nREGELN:"
    "\n1. FAKTEN-TREUE: Der Antragstext ist die absolute Wahrheit. Wenn dort steht 'Anhang vorhanden' oder '[x]', dann IST das Dokument da."
    "\n2. ABGLEICH: Bewerte Zahlen (Noten, Geld) NUR anhand der Richtlinie."
    "\n3. SCORING: Starte bei 100. Ziehe Punkte ab für Dinge, die den Richtlinien WIDERSPRECHEN oder FEHLEN, beziehungsweise für unseriöse Anträge etc."
    "\n\nOUTPUT:"
    "\nAntworte extrem kurz."
    "\nGib nur den Score von 0-100 aus."
)

def build_prompt_from_file(guidelines: str = "",
                           cv_header: str = "",
                           cv_body: str = "",
                           cv_body2: str = "",
                           name: str = "",
                           gender: str = "",
                           address: str = "",
                           email: str = "",
                           date_of_birth: str = "",
                           nationality: str = "") -> str:
    guidelines_part = ""
    if guidelines:
        guidelines_part = f"\nNUTZE FOLGENDE RICHTLINIEN ZUR BEWERTUNG (Verbindlich):\n{guidelines}\n"

    details = []


    details.append("BEWERBUNG UM EIN LEISTUNGSSTIPENDIUM im Studienjahr 2024/2025")
    if name:
        details.append(f"Vor-/Nachname: {name}")
    if gender:
        details.append(f"Geschlecht: {gender}")
    details.append(f"Studienrichtung: Artificial Intelligence, Studienkennzahl: UD 033 536")
    if address:
        details.append(f"Anschrift: {address}")
    if email:
        details.append(f"E-mail: {email}")
    if date_of_birth:
        details.append(f"Geburtsdatum: {date_of_birth}")
    if nationality:
        details.append(f"Staatsbürgerschaft: {nationality}")
    if cv_body:
        details.append(cv_body)
    details.append((f"{name} (elektronisch signiert"))
    if cv_body2:
        details.append(cv_body2)
    details.append(f"{name}")


    full_cv_text = "\n".join(details)

    return f"""{SYSTEM_MESSAGE}

{guidelines_part} 
Hier ist der zu bewertende Antrag:
--------------------------------------------------
{full_cv_text}
--------------------------------------------------

### ERGEBNIS
Der finale Score (0-100) beträgt:"""