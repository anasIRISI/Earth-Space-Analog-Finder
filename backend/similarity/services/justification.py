LIBELLES = {
    "pente_moy":           ("la pente moyenne", "°", 1),
    "rugosite_moy":        ("la rugosité", " m", 0),
    "relief_local":        ("le relief local", " m", 0),
    "albedo_moy":          ("l'albédo", "", 2),
    "ati_moy":             ("l'inertie thermique apparente", "", 1),
    "amplitude_thermique": ("l'amplitude thermique jour/nuit", " K", 0),
    "indice_fer":          ("l'indice d'oxydes de fer", "", 2),
}


def _fmt(champ, v):
    _, unite, nd = LIBELLES[champ]
    return f"{v:.{nd}f}{unite}"


def qualifier(score):
    if score >= 85:
        return "analogue excellent"
    if score >= 70:
        return "bon analogue"
    if score >= 50:
        return "analogue partiel"
    return "analogue faible"


def generer_justification(profil_mars, cellule, detail, score):
    """Texte explicatif à partir des scores par critère (règles simples)."""
    proches, differents = [], []
    for champ, s in sorted(detail.items(), key=lambda kv: kv[1], reverse=True):
        txt = (f"{LIBELLES[champ][0]} ({_fmt(champ, profil_mars[champ])} sur Mars, "
               f"{_fmt(champ, getattr(cellule, champ))} ici)")
        if s >= 0.8:
            proches.append(txt)
        elif s < 0.6:
            differents.append(txt)

    phrases = [f"Score {score:.0f}/100 : {qualifier(score)}."]
    if proches:
        phrases.append("Ressemblances : " + " ; ".join(proches) + ".")
    if differents:
        phrases.append("Différences notables : " + " ; ".join(differents) + ".")
    manquants = [LIBELLES[c][0] for c in LIBELLES if c not in detail]
    if manquants:
        phrases.append("Non comparés (données absentes d'un côté) : "
                       + ", ".join(manquants) + ".")
    if cellule.homogeneite is not None:
        phrases.append(f"Homogénéité de la zone terrestre : {cellule.homogeneite:.2f} "
                       "(1 = très homogène).")
    return " ".join(phrases)