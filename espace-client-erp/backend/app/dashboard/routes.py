from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models_erp import (
    Utilisateur,
    Commande,
    Facture,
    Document,
    NotificationErp,
    Depense,
    CompteBancaire,
    FactureAchat,
)

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")


@dashboard_bp.get("/summary")
@jwt_required()
def summary():
    """
    4.2 Tableau de bord — agrège en un seul appel :
    nom du client, solde, dernières commandes, dernières factures,
    notifications, statut des commandes, documents récents.

    Lit directement les tables locales (client, commande, facture, document,
    notification) désormais partagées avec le schéma ERP.
    """
    utilisateur = Utilisateur.query.get(int(get_jwt_identity()))
    if not utilisateur:
        return jsonify({"errors": {"general": "Utilisateur introuvable."}}), 404

    result = {
        "customer_name": utilisateur.nom,
        "erp_linked": utilisateur.client_id is not None,
        "balance": None,
        "recent_orders": [],
        "recent_invoices": [],
        "recent_documents": [],
        "order_status_summary": {},
        "notifications": [],
        "erp_errors": [],
    }

    # Notifications : toujours disponibles
    notifications = (
        NotificationErp.query.filter_by(utilisateur_id=utilisateur.id)
        .order_by(NotificationErp.created_at.desc())
        .limit(10)
        .all()
    )
    result["notifications"] = [
        {
            "id": n.id,
            "type": n.type,
            "title": n.titre,
            "message": n.message,
            "link": n.lien,
            "is_read": n.est_lu,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in notifications
    ]
    result["unread_notifications_count"] = NotificationErp.query.filter_by(
        utilisateur_id=utilisateur.id, est_lu=False
    ).count()

    # ------------------------------------------------------------
    # Cartes financières (globales à l'entreprise, pas filtrées par
    # client) : Factures Ventes, Factures d'achats, Dépenses,
    # Marge brute/nette, Comptes bancaires, Solde de trésorerie.
    # Toujours calculées, même si le compte n'est pas encore relié
    # à une fiche client.
    # ------------------------------------------------------------
    factures_ventes_total = (
        db.session.query(db.func.coalesce(db.func.sum(Facture.total_ttc), 0))
        .filter(Facture.est_supprime.is_(False))
        .scalar()
    )
    factures_achats_total = (
        db.session.query(db.func.coalesce(db.func.sum(FactureAchat.montant_ttc), 0))
        .filter(FactureAchat.est_supprime.is_(False))
        .scalar()
    )
    depenses_total = (
        db.session.query(db.func.coalesce(db.func.sum(Depense.montant), 0))
        .filter(Depense.est_supprime.is_(False))
        .scalar()
    )

    marge_brute = float(factures_ventes_total) - float(factures_achats_total)
    marge_nette = marge_brute - float(depenses_total)

    comptes = CompteBancaire.query.filter_by(est_supprime=False).all()
    comptes_list = [
        {"id": c.id, "nom_banque": c.nom_banque, "solde": float(c.solde)} for c in comptes
    ]
    solde_tresorerie = sum(c["solde"] for c in comptes_list)

    result["finance"] = {
        "factures_ventes_total": float(factures_ventes_total),
        "factures_achats_total": float(factures_achats_total),
        "depenses_total": float(depenses_total),
        "marge_brute": marge_brute,
        "marge_nette": marge_nette,
        "comptes_bancaires": comptes_list,
        "solde_tresorerie_actuelle": solde_tresorerie,
        "currency": "TND",
    }

    if not utilisateur.client_id:
        result["erp_errors"].append(
            "Votre compte n'est pas encore relié à une fiche client."
        )
        return jsonify(result)

    client_id = utilisateur.client_id

    # --- Solde du compte : somme des soldes dus sur les factures non soldées ---
    factures_non_soldees = Facture.query.filter_by(
        client_id=client_id, est_supprime=False, est_solder=False
    ).all()
    solde_total = sum((f.solde_du or 0) for f in factures_non_soldees)
    result["balance"] = {"balance": float(solde_total), "currency": "TND"}

    # --- Dernières commandes ---
    commandes = (
        Commande.query.filter_by(client_id=client_id, est_supprime=False)
        .order_by(Commande.date_commande.desc())
        .limit(5)
        .all()
    )
    result["recent_orders"] = [
        {
            "id": c.id,
            "reference": c.numero,
            "date": c.date_commande.isoformat() if c.date_commande else None,
            "status": str(c.status_id) if c.status_id is not None else "inconnu",
            "total": float(c.total_ttc) if c.total_ttc is not None else 0,
        }
        for c in commandes
    ]

    # --- Statut des commandes (répartition) ---
    status_summary: dict[str, int] = {}
    toutes_commandes = Commande.query.filter_by(client_id=client_id, est_supprime=False).all()
    for c in toutes_commandes:
        key = str(c.status_id) if c.status_id is not None else "inconnu"
        status_summary[key] = status_summary.get(key, 0) + 1
    result["order_status_summary"] = status_summary

    # --- Dernières factures ---
    factures = (
        Facture.query.filter_by(client_id=client_id, est_supprime=False)
        .order_by(Facture.date_facture.desc())
        .limit(5)
        .all()
    )
    result["recent_invoices"] = [
        {
            "id": f.id,
            "number": f.numero,
            "date": f.date_facture.isoformat() if f.date_facture else None,
            "due_date": f.date_echeance.isoformat() if f.date_echeance else None,
            "amount": float(f.total_ttc) if f.total_ttc is not None else 0,
            "payment_status": "soldée" if f.est_solder else "en attente",
        }
        for f in factures
    ]

    # --- Documents récents ---
    documents = (
        Document.query.filter_by(client_id=client_id, est_supprime=False)
        .order_by(Document.id.desc())
        .limit(5)
        .all()
    )
    result["recent_documents"] = [
        {
            "id": d.id,
            "type": "document",
            "name": d.nom,
            "date": None,
            "download_url": d.lien,
        }
        for d in documents
    ]

    return jsonify(result)


@dashboard_bp.post("/notifications/<int:notification_id>/read")
@jwt_required()
def mark_notification_read(notification_id: int):
    """Marque une notification comme lue (utilisé par le dashboard)."""
    utilisateur_id = int(get_jwt_identity())
    notification = NotificationErp.query.filter_by(
        id=notification_id, utilisateur_id=utilisateur_id
    ).first()
    if not notification:
        return jsonify({"errors": {"general": "Notification introuvable."}}), 404

    notification.est_lu = True
    db.session.commit()

    return jsonify({"message": "Notification marquée comme lue."})
