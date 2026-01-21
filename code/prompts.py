SYSTEM_MESSAGE = (
    "Du bist ein spezialisierter Algorithmus zur Berechnung von 'Bedürftigkeits-Scores' für das ÖH Sozialstipendium. "
    "Deine Aufgabe ist es, Anträge rein nach ihrer finanziellen DRINGLICHKEIT zu bewerten."
    "\n\nACHTUNG - LOGIK-INVERSION (WICHTIG!):"
    "\n- Geldmangel = HOHE PUNKTEZAHL (Stipendium wird dringend benötigt)."
    "\n- Überschuss = NIEDRIGE PUNKTEZAHL (Kein Stipendium nötig)."
    "\n\nDEIN RECHENWEG:"
    "\n1. Suche nach Einnahmen und Ausgaben."
    "\n2. Berechne: Einnahmen MINUS Ausgaben."
    "\n   -> Ergebnis NEGATIV (Defizit): Score MUSS im Bereich 75-100 liegen."
    "\n   -> Ergebnis NULL oder KNAPP POSITIV (0€ bis 50€ Plus): Score im Bereich 40-74."
    "\n   -> Ergebnis DEUTLICH POSITIV (> 50€ Plus): Score im Bereich 0-39."
    "\n3. Wenn KEINE ZAHLEN da sind: Schätze die Notlage anhand des Textes (In dubio pro reo)."
    "\n\nBEWERTUNGS-SKALA (Synchronisiert):"
    "\n- 90-100 Punkte: AKUTE EXISTENZBEDROHUNG (Defizit > 200€, Schulden, Miete offen)."
    "\n- 75-89 Punkte: DEFIZIT VORHANDEN (Defizit 1€ bis 200€). Jedes Minus am Konto rechtfertigt diesen hohen Score!"
    "\n- 40-74 Punkte: KNAPP / AUSGEGLICHEN (0€ bis 50€ Überschuss). Kommt gerade so durch."
    "\n- 0-39 Punkte: KOMFORTABEL / REICH (Mehr als 50€ Überschuss, Luxusausgaben, Urlaub)."
    "\n\nGib als Output NUR die Zahl (0-100) aus. Keine Rechnung, kein Text."
)

def build_prompt_from_file(guidelines: str = "",
                           cv_header: str = "",
                           cv_body: str = "",
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

    if cv_header:
        details.append(cv_header)
    if name:
        details.append(f"Vor-/Nachname: {name}")
    if gender:
        details.append(f"Geschlecht: {gender}")
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

    full_cv_text = "\n".join(details)

    return f"""{SYSTEM_MESSAGE}

{guidelines_part} 
Hier ist der zu bewertende Antrag:
--------------------------------------------------
{full_cv_text}
--------------------------------------------------

### ERGEBNIS
Der finale Score (0-100) beträgt:"""