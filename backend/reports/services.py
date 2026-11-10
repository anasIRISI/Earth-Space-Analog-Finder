import io
from datetime import datetime
from xml.sax.saxutils import escape

from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

ROUGE = colors.HexColor("#c1440e")

CRITERES = {   # champ : (libellé court, unité, décimales)
    "pente_moy": ("Pente moyenne", "°", 1),
    "rugosite_moy": ("Rugosité", " m", 0),
    "relief_local": ("Relief local", " m", 0),
    "albedo_moy": ("Albédo", "", 2),
    "ati_moy": ("Inertie thermique app.", "", 1),
    "amplitude_thermique": ("Amplitude thermique", " K", 0),
    "indice_fer": ("Indice oxydes de fer", "", 2),
}
OBJECTIFS = {"rover": "Mobilité rover", "habitat": "Habitat", "isru": "Ressources (ISRU)"}


def _fmt(champ, v):
    if v is None:
        return "n/d"
    _, unite, nd = CRITERES[champ]
    return f"{v:.{nd}f}{unite}"


def _p(texte, style):
    return Paragraph(escape(str(texte)), style)


def _graphique(detail):
    items = sorted(detail.items(), key=lambda kv: kv[1])
    if not items:
        return None
    h = 22 * len(items)
    d = Drawing(440, h + 25)
    ch = HorizontalBarChart()
    ch.x, ch.y, ch.width, ch.height = 150, 12, 260, h
    ch.data = [[round(v * 100) for _, v in items]]
    ch.categoryAxis.categoryNames = [CRITERES[k][0] for k, _ in items]
    ch.categoryAxis.labels.fontSize = 8
    ch.valueAxis.valueMin, ch.valueAxis.valueMax, ch.valueAxis.valueStep = 0, 100, 25
    ch.valueAxis.labels.fontSize = 8
    ch.bars[0].fillColor = ROUGE
    d.add(ch)
    return d


def _pied_de_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(2 * cm, 1.2 * cm, "Earth-Space Analog Finder – rapport automatique")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def generer_pdf(recherche, top_detail=3):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=2 * cm, bottomMargin=2 * cm,
                            title=f"Rapport d'analogues #{recherche.pk}")
    base = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=base["Title"], textColor=ROUGE)
    h2 = ParagraphStyle("h2", parent=base["Heading2"], textColor=ROUGE)
    txt = ParagraphStyle("txt", parent=base["BodyText"], fontSize=9.5, leading=13)
    petit = ParagraphStyle("petit", parent=txt, fontSize=8, textColor=colors.grey)
    cell = ParagraphStyle("cell", parent=txt, fontSize=8.5, leading=10)

    sel = recherche.selection
    resultats = list(recherche.resultats.select_related("cellule").order_by("rang"))
    e = []

    # --- En-tête
    e += [Paragraph("Rapport d'analogues terrestres", h1),
          _p(f"Zone martienne sélectionnée – objectif : "
             f"{OBJECTIFS.get(recherche.objectif, recherche.objectif)}", txt),
          _p(f"Généré le {datetime.now():%d/%m/%Y à %H:%M} – recherche n° {recherche.pk}", petit),
          Spacer(1, 12)]

    # --- Zone de Mars
    c = sel.geom.centroid
    e += [Paragraph("1. Zone étudiée sur Mars", h2),
          _p(f"Centre : {c.y:.2f}° N, {c.x:.2f}° E – surface : {sel.surface_km2:,.0f} km²", txt),
          Spacer(1, 6)]
    lignes = [["Critère", "Valeur sur Mars"]] + [
        [CRITERES[k][0], _fmt(k, getattr(sel, k))] for k in CRITERES]
    t = Table(lignes, colWidths=[8 * cm, 5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ROUGE), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f1ee")])]))
    e += [t, Spacer(1, 12)]

    # --- Classement
    e.append(Paragraph("2. Meilleurs analogues terrestres", h2))
    lignes = [["Rang", "Cellule", "Pays", "Centre (lat, lon)", "Score"]]
    for r in resultats:
        ce = r.cellule.geom.centroid
        lignes.append([str(r.rang), _p(r.cellule.cell_id, cell),
                       _p(r.cellule.pays or "–", cell),
                       f"{ce.y:.2f}, {ce.x:.2f}", f"{r.score_global:.1f}"])
    t = Table(lignes, colWidths=[1.3 * cm, 5 * cm, 3 * cm, 4.2 * cm, 2 * cm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ROUGE), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.lightgrey)]))
    e += [t, Spacer(1, 12)]

    # --- Détail des premiers résultats
    e.append(Paragraph("3. Analyse détaillée des meilleurs résultats", h2))
    for r in resultats[:top_detail]:
        ce = r.cellule.geom.centroid
        bloc = [_p(f"#{r.rang} – {r.cellule.cell_id} ({ce.y:.2f}, {ce.x:.2f}) – "
                   f"score {r.score_global:.1f}/100", base["Heading3"]),
                _p(r.justification, txt)]
        g = _graphique(r.scores_criteres or {})
        if g:
            bloc += [_p("Similarité par critère (%)", petit), g]
        e += [KeepTogether(bloc), Spacer(1, 10)]

    # --- Méthode et limites
    e += [Paragraph("4. Méthode, sources et limites", h2),
          _p("Chaque critère est comparé entre la zone martienne et chaque cellule terrestre "
             "(similarité de 0 à 1 selon l'écart normalisé), pondéré selon l'objectif choisi, "
             "puis combiné en un score de 0 à 100 avec un léger bonus d'homogénéité. Les critères "
             "absents d'un côté sont ignorés, pas pénalisés.", txt),
          _p("Sources : Mars – MOLA (relief), MGS TES (albédo). Terre – NASADEM ou Copernicus "
             "GLO-30 (relief), MODIS (albédo, température), TerraClimate (aridité), traitées avec "
             "Google Earth Engine.", txt),
          _p("Limites : on compare des caractéristiques de surface, pas l'atmosphère, la gravité "
             "ni la radiation. Les cellules terrestres sont plus grandes que la zone martienne "
             "étudiée, donc les moyennes sont comparables mais pas les variations internes. "
             "L'inertie thermique et la minéralogie ne sont comparées que si elles sont "
             "disponibles (voir « Non comparés » dans chaque justification). Un score élevé "
             "indique une ressemblance, pas une équivalence : une validation sur site reste "
             "nécessaire.", txt)]

    doc.build(e, onFirstPage=_pied_de_page, onLaterPages=_pied_de_page)
    return buf.getvalue()