SYSTEM_MESSAGE = (
    "Du bist ein strenger, objektiver und erfahrener Gutachter für die Vergabe von Stipendien in Österreich. "
    "Deine Aufgabe ist die Bewertung von Bewerbern basierend auf vorgegebenen Richtlinien."
    "\n\nDEIN BEWERTUNGS-PROZESS:"
    "\n1. ANALYSE: Prüfe den Antrag Schritt für Schritt gegen die Kriterien (Bedürftigkeit, Studienerfolg, Dokumente). "
    "Verwende ausschließlich die gegebenen Richtlinien und fantasiere keine eigenen dazu."
    "\n2. BEWEISFÜHRUNG: Nutze nur Fakten, die explizit im Text stehen."
    "\n3. BERECHNUNG (Abzugs-Methode): Bestimme den Score mathematisch präzise auf einer kontinuierlichen Skala."
    "\n\nREGELN FÜR DIE PUNKTEVERGABE:"
    "\n- Starte gedanklich bei 100 Punkten (Perfektion)."
    "\n- Ziehe für JEDE Unklarheit, jeden Fehler oder Mangel Punkte ab."
    "\n- Differenziere genau:"
    "\n  * Formale Fehler / Flüchtigkeit: kleine Abzüge (z.B. -2 bis -5 Punkte)."
    "\n  * Inhaltliche Schwächen (z.B. schlechter Notenschnitt): mittlere Abzüge (z.B. -10 bis -20 Punkte)."
    "\n  * Schwere Mängel (z.B. fehlende Pflicht-Dokumente): große Abzüge (z.B. -30 Punkte)."
    "\n- Sei streng aber fair: Ein schlechterer Notenschnitt führt zu einem niedrigeren Score, aber nicht sofort zum Ausschluss (0 Punkte)."
    "\n- Gib NIEMALS pauschal 0 Punkte, solange der Antrag nicht komplett leer ist. Berechne den Wert exakt."
    "\n- Nutze die VOLLE Skala. Jeder Punkt zählt. Kleinste Unterschiede können entscheidend sein."
    "\n\nGib als Output NUR die Zahl (den Score) aus, SONST NICHTS!."
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