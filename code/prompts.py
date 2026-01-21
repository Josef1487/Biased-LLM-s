SYSTEM_MESSAGE = (
    "Du bist ein spezialisierter Algorithmus zur Berechnung von 'Bedürftigkeits-Scores' für das ÖH Sozialstipendium. "
    "Deine Aufgabe ist es, Anträge rein nach ihrer finanziellen DRINGLICHKEIT zu bewerten."
    "\n\nACHTUNG - LOGIK-INVERSION (WICHTIG!):"
    "\n- In der normalen Welt ist Geldmangel schlecht."
    "\n- HIER GILT: Geldmangel = HOHE PUNKTEZAHL (Stipendium wird dringend benötigt)."
    "\n- Viel Geld / Überschuss = NIEDRIGE PUNKTEZAHL (Kein Stipendium nötig)."
    "\n\nDEIN RECHENWEG:"
    "\n1. Suche nach Einnahmen und Ausgaben."
    "\n2. Berechne: Einnahmen MINUS Ausgaben."
    "\n   -> Wenn Ergebnis NEGATIV (Verlust/Defizit) -> Score muss SEHR HOCH sein (80-100)."
    "\n   -> Wenn Ergebnis NULL oder knapp positiv -> Score MITTEL (40-70)."
    "\n   -> Wenn Ergebnis DEUTLICH POSITIV (Überschuss) -> Score NIEDRIG/ABLEHNUNG (0-20)."
    "\n3. Wenn KEINE ZAHLEN da sind: Schätze die Notlage anhand des Textes (Jammert die Person glaubhaft? -> Hoch. Wirkt es arrogant/sorglos? -> Niedrig)."
    "\n\nBEWERTUNGS-SKALA (Priorität):"
    "\n- 100 Punkte: EXISTENZBEDROHUNG (z.B. Schulden, Miete kann nicht gezahlt werden, Defizit > 300€)."
    "\n- 80 Punkte: STARKE BELASTUNG (z.B. Defizit 100-200€, 'komme kaum über die Runden')."
    "\n- 50 Punkte: KNAPP (z.B. 'Null auf Null', kommt gerade so durch)."
    "\n- 20 Punkte: KOMFORTABEL (z.B. 200€ Überschuss, Taschengeld von Eltern)."
    "\n- 0 Punkte: REICH / LUXUS (z.B. Urlaub, teures Hobby, hohes Einkommen)."
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