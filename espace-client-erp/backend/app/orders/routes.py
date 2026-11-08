from flask import Blueprint, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models_erp import Utilisateur, Commande, HistoriqueStatutCommande
from app.utils.pdf_export import generate_commande_pdf

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


def _current_client_id():
    utilisateur = Utilisateur.query.get(int(get_jwt_identity()))
    if not utilisateur or not utilisateur.client_id:
        return None, None
    return utilisateur, utilisateur.client_id


@orders_bp.get("")
@jwt_required()
def list_orders():
    """4.4 Liste des commandes du client connecté (avec statut)."""
    _, client_id = _current_client_id()
    if not client_id:
        return jsonify({"orders": [], "erp_errors": ["Compte non relié à une fiche client."]})

    commandes = (
        Commande.query.filter_by(client_id=client_id, est_supprime=False)
        .order_by(Commande.date_commande.desc())
        .all()
    )
    return jsonify({"orders": [c.to_dict() for c in commandes]})


@orders_bp.get("/<int:order_id>")
@jwt_required()
def get_order(order_id: int):
    """4.4 Détail d'une commande : lignes + statut + historique des statuts."""
    _, client_id = _current_client_id()
    if not client_id:
        return jsonify({"errors": {"general": "Compte non relié à une fiche client."}}), 404

    commande = Commande.query.filter_by(id=order_id, client_id=client_id, est_supprime=False).first()
    if not commande:
        return jsonify({"errors": {"general": "Commande introuvable."}}), 404

    lignes = [
        {
            "nom_article": l.nom_article,
            "reference": l.reference,
            "quantite": float(l.quantite) if l.quantite is not None else 0,
            "prix_ht": float(l.prix_ht) if l.prix_ht is not None else 0,
            "total_prix_ttc": float(l.total_prix_ttc) if l.total_prix_ttc is not None else 0,
        }
        for l in commande.lignes.filter_by(est_supprime=False).all()
    ]

    historique = [
        {
            "ancien_status_id": h.ancien_status_id,
            "nouveau_status_id": h.nouveau_status_id,
            "date_changement": h.date_changement.isoformat() if h.date_changement else None,
            "commentaire": h.commentaire,
        }
        for h in commande.historique_statuts.order_by(HistoriqueStatutCommande.date_changement.asc()).all()
    ]

    data = commande.to_dict()
    data["lignes"] = lignes
    data["historique_statuts"] = historique
    return jsonify({"order": data})


@orders_bp.get("/<int:order_id>/pdf")
@jwt_required()
def download_order_pdf(order_id: int):
    """Export PDF du bon de commande."""
    utilisateur, client_id = _current_client_id()
    if not client_id:
        return jsonify({"errors": {"general": "Compte non relié à une fiche client."}}), 404

    commande = Commande.query.filter_by(id=order_id, client_id=client_id, est_supprime=False).first()
    if not commande:
        return jsonify({"errors": {"general": "Commande introuvable."}}), 404

    pdf_buffer = generate_commande_pdf(commande, utilisateur.client)
    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"commande_{commande.numero}.pdf",
    )
