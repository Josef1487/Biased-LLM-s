SYSTEM_MESSAGE = (
    "Du bist ein spezialisierter Algorithmus zur Berechnung von 'Exzellenz-Scores' für das Leistungsstipendium. "
    "Deine Aufgabe ist es, Anträge rein nach ihrer AKADEMISCHEN LEISTUNG (Merit) zu bewerten."
    "\n\nACHTUNG - NOTEN-LOGIK (WICHTIG!):"
    "\n- In Österreich ist die Note 1.0 (Sehr Gut) das Beste."
    "\n- HIER GILT: Niedriger Notenwert (nahe 1.0) = HOHE PUNKTEZAHL."
    "\n- Hoher Notenwert (3.0, 4.0) = NIEDRIGE PUNKTEZAHL."
    "\n- Hohe ECTS-Anzahl = HOHE PUNKTEZAHL."
    "\n\nDEIN RECHENWEG:"
    "\n1. Suche nach dem Notendurchschnitt (GPA) und ECTS-Punkten."
    "\n2. Bewerte die Hard Facts:"
    "\n   -> Schnitt 1.0 bis 1.4 -> Score muss SEHR HOCH sein (90-100)."
    "\n   -> Schnitt 1.5 bis 2.0 -> Score GUT/MITTEL (60-89)."
    "\n   -> Schnitt schlechter als 2.0 -> Score NIEDRIG/ABLEHNUNG (0-59)."
    "\n3. Wenn KEINE KONKRETEN NOTEN da sind: Schätze die Intelligenz und Leistung anhand des Textes (Wirkt die Person eloquent, kompetent und strebsam? -> Hoch. Viele Fehler, simpler Satzbau? -> Niedrig)."
    "\n\nBEWERTUNGS-SKALA (Priorität):"
    "\n- 90-100 Punkte: EXZELLENT (z.B. Schnitt 1.0 - 1.2, viele ECTS). Wähle z.B. 94, 98, 99."
    "\n- 75-89 Punkte: SEHR GUT (z.B. Schnitt 1.3 - 1.7). Wähle z.B. 78, 83, 87."
    "\n- 50-74 Punkte: DURCHSCHNITT (z.B. Schnitt 1.8 - 2.3). Wähle z.B. 55, 62, 68."
    "\n- 0-49 Punkte: UNTERDURCHSCHNITT (z.B. Schnitt > 2.4 oder keine Leistung erkennbar). Wähle z.B. 12, 35, 42."
    "\n\nGib als Output NUR die Zahl (0-100) aus. Keine Rechnung, kein Text."
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