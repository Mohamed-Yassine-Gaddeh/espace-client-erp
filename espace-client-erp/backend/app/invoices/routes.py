from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models_erp import Utilisateur, Facture
from app.utils.pdf_export import generate_facture_pdf

invoices_bp = Blueprint("invoices", __name__, url_prefix="/api/invoices")


def _current_client_id():
    utilisateur = Utilisateur.query.get(int(get_jwt_identity()))
    if not utilisateur or not utilisateur.client_id:
        return None, None
    return utilisateur, utilisateur.client_id


@invoices_bp.get("")
@jwt_required()
def list_invoices():
    """4.5 Liste des factures du client connecté."""
    _, client_id = _current_client_id()
    if not client_id:
        return jsonify({"invoices": [], "erp_errors": ["Compte non relié à une fiche client."]})

    factures = (
        Facture.query.filter_by(client_id=client_id, est_supprime=False)
        .order_by(Facture.date_facture.desc())
        .all()
    )
    return jsonify({"invoices": [f.to_dict() for f in factures]})


@invoices_bp.get("/<int:invoice_id>")
@jwt_required()
def get_invoice(invoice_id: int):
    """4.5 Détail d'une facture : lignes + état de paiement."""
    _, client_id = _current_client_id()
    if not client_id:
        return jsonify({"errors": {"general": "Compte non relié à une fiche client."}}), 404

    facture = Facture.query.filter_by(id=invoice_id, client_id=client_id, est_supprime=False).first()
    if not facture:
        return jsonify({"errors": {"general": "Facture introuvable."}}), 404

    lignes = [
        {
            "nom_article": l.nom_article,
            "reference": l.reference,
            "quantite": float(l.quantite) if l.quantite is not None else 0,
            "prix_ht": float(l.prix_ht) if l.prix_ht is not None else 0,
            "total_prix_ttc": float(l.total_prix_ttc) if l.total_prix_ttc is not None else 0,
        }
        for l in facture.lignes.filter_by(est_supprime=False).all()
    ]

    data = facture.to_dict()
    data["lignes"] = lignes
    return jsonify({"invoice": data})


@invoices_bp.get("/<int:invoice_id>/pdf")
@jwt_required()
def download_invoice_pdf(invoice_id: int):
    """Export PDF de la facture."""
    utilisateur, client_id = _current_client_id()
    if not client_id:
        return jsonify({"errors": {"general": "Compte non relié à une fiche client."}}), 404

    facture = Facture.query.filter_by(id=invoice_id, client_id=client_id, est_supprime=False).first()
    if not facture:
        return jsonify({"errors": {"general": "Facture introuvable."}}), 404

    pdf_buffer = generate_facture_pdf(facture, utilisateur.client)
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"facture_{facture.numero}.pdf",
    )
