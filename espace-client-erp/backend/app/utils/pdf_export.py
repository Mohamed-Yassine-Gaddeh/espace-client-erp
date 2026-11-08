"""
Génération de PDF pour les commandes et factures, via reportlab
(voir /mnt/skills/public/pdf/SKILL.md — reportlab est l'outil recommandé
pour la création de PDF).
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def _fmt(v) -> str:
    try:
        return f"{float(v):.3f}"
    except (TypeError, ValueError):
        return "0.000"


def _build_pdf(title: str, numero: str, date_str: str, client, lignes: list, totaux: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitreDoc", parent=styles["Title"], fontSize=18, spaceAfter=4, textColor=colors.HexColor("#16213e")
    )
    normal = styles["Normal"]

    story = []
    story.append(Paragraph(title, title_style))
    story.append(Paragraph(f"N° {numero}", normal))
    story.append(Paragraph(f"Date : {date_str}", normal))
    story.append(Spacer(1, 12))

    if client:
        story.append(Paragraph(f"<b>Client :</b> {client.nom}", normal))
        if client.email:
            story.append(Paragraph(f"Email : {client.email}", normal))
        if client.telephone:
            story.append(Paragraph(f"Téléphone : {client.telephone}", normal))
        if client.numero_tva:
            story.append(Paragraph(f"N° TVA : {client.numero_tva}", normal))
    story.append(Spacer(1, 16))

    # Tableau des lignes
    data = [["Article", "Qté", "Prix U. HT", "TVA %", "Total TTC"]]
    for ligne in lignes:
        data.append(
            [
                ligne.get("nom_article") or "-",
                _fmt(ligne.get("quantite")),
                _fmt(ligne.get("prix_ht")),
                _fmt(ligne.get("taux_tva")),
                _fmt(ligne.get("total_prix_ttc")),
            ]
        )

    table = Table(data, colWidths=[70 * mm, 25 * mm, 30 * mm, 25 * mm, 30 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c4a7c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd3e0")),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f8fb")]),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 16))

    # Totaux
    totaux_data = [
        ["Total HT", _fmt(totaux.get("total_ht")) + " TND"],
        ["Total TVA", _fmt(totaux.get("total_tva")) + " TND"],
        ["Total TTC", _fmt(totaux.get("total_ttc")) + " TND"],
    ]
    totaux_table = Table(totaux_data, colWidths=[40 * mm, 40 * mm], hAlign="RIGHT")
    totaux_table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
                ("LINEABOVE", (0, -1), (-1, -1), 0.75, colors.HexColor("#16213e")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(totaux_table)

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_commande_pdf(commande, client) -> io.BytesIO:
    lignes = [
        {
            "nom_article": l.nom_article,
            "quantite": l.quantite,
            "prix_ht": l.prix_ht,
            "taux_tva": l.taux_tva,
            "total_prix_ttc": l.total_prix_ttc,
        }
        for l in commande.lignes.filter_by(est_supprime=False, est_commentaire=False).all()
    ]
    totaux = {
        "total_ht": commande.total_ht,
        "total_tva": commande.total_tva,
        "total_ttc": commande.total_ttc,
    }
    date_str = commande.date_commande.strftime("%d/%m/%Y") if commande.date_commande else "-"
    return _build_pdf("Bon de commande", commande.numero, date_str, client, lignes, totaux)


def generate_facture_pdf(facture, client) -> io.BytesIO:
    lignes = [
        {
            "nom_article": l.nom_article,
            "quantite": l.quantite,
            "prix_ht": l.prix_ht,
            "taux_tva": l.taux_tva,
            "total_prix_ttc": l.total_prix_ttc,
        }
        for l in facture.lignes.filter_by(est_supprime=False, est_commentaire=False).all()
    ]
    totaux = {
        "total_ht": facture.total_ht,
        "total_tva": facture.total_tva,
        "total_ttc": facture.total_ttc,
    }
    date_str = facture.date_facture.strftime("%d/%m/%Y") if facture.date_facture else "-"
    return _build_pdf("Facture", facture.numero, date_str, client, lignes, totaux)
