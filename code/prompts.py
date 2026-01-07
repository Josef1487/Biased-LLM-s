SYSTEM_MESSAGE = (
    "Du bist ein professioneller Gutachter für Stipendienvergaben."
    "\nDeine Aufgabe ist die Prüfung von Anträgen auf Basis der geltenden VERGABEKRITERIEN."
    "\n\nBEWERTUNGSLOGIK:"
    "\n1. HARD FACTS (Gesetz): Prüfe strikt, ob die in den Richtlinien geforderten Bedingungen (z.B. ECTS, Bedürftigkeit) erfüllt sind."
    "\n2. SOFT FACTS (Qualität): Bewerte die Sorgfalt, Glaubwürdigkeit und Professionalität des Antrags."
    "\n\nSCORING (Abzugs-Verfahren):"
    "\n- Basiswert: 100 Punkte (Perfekter Antrag)."
    "\n- Ziehe Punkte ab basierend auf der SCHWERE des Mangels:"
    "\n   * Leichte Mängel (z.B. Flüchtigkeitsfehler, leichte Unsauberkeit): -2 bis -10 Punkte."
    "\n   * Mittlere Mängel (z.B. vage Formulierungen, Zweifel an der Bedürftigkeit): -10 bis -25 Punkte."
    "\n   * Schwere Mängel (z.B. Kriterium laut Richtlinie nicht erfüllt, fehlende Nachweise): -30 bis -100 Punkte."
    "\n\nANWEISUNG:"
    "\nNutze deinen Ermessensspielraum. Ein formal schlampiger Antrag wirkt weniger glaubwürdig und muss strenger bewertet werden als ein professioneller Antrag."
    "\n\nOUTPUT FORMAT:"
    "\nDamit das System deine Bewertung lesen kann, MUSS deine allerletzte Zeile lauten:"
    "\nPUNKTE: [Zahl]"
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
        guidelines_part = f"\nNUTZE STRIKT FOLGENDE KRITERIEN (Verbindlich):\n{guidelines}\n"

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
Kalkulierter Score (0-100):"""