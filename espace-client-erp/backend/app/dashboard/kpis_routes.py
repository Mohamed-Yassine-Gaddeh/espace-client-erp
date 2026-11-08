"""
Endpoint dédié au dashboard ERP "moderne" : KPIs avec variation mensuelle,
séries mensuelles pour les graphiques, meilleurs clients, articles les
plus vendus, dernières factures/commandes.

Un seul endpoint (comme /api/dashboard/summary) pour respecter la
contrainte de performance : un seul appel réseau depuis le frontend.

Toutes les données sont réelles (calculées depuis les tables existantes) :
si aucune donnée n'a été saisie, les valeurs sont à 0, jamais inventées.
"""

from datetime import datetime, timedelta
from calendar import month_name

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models_erp import (
    Client,
    Commande,
    Facture,
    FactureAchat,
    Depense,
    CompteBancaire,
    Article,
    ArticleFacture,
    Utilisateur,
)

dashboard_kpis_bp = Blueprint("dashboard_kpis", __name__, url_prefix="/api/dashboard")


def _month_bounds(offset_months: int = 0):
    """Renvoie (début, fin) du mois courant moins `offset_months` mois."""
    today = datetime.utcnow()
    year = today.year
    month = today.month - offset_months
    while month <= 0:
        month += 12
        year -= 1
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    return start, end


def _variation(current: float, previous: float) -> float | None:
    """Variation en % ; None si le mois précédent est à 0 (division impossible)."""
    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 1)


@dashboard_kpis_bp.get("/erp-overview")
@jwt_required()
def erp_overview():
    now_start, now_end = _month_bounds(0)
    prev_start, prev_end = _month_bounds(1)

    # ------------------------------------------------------------
    # KPIs avec variation vs mois précédent
    # ------------------------------------------------------------
    ca_mois = (
        db.session.query(func.coalesce(func.sum(Facture.total_ttc), 0))
        .filter(Facture.est_supprime.is_(False), Facture.date_facture >= now_start, Facture.date_facture < now_end)
        .scalar()
    )
    ca_mois_prec = (
        db.session.query(func.coalesce(func.sum(Facture.total_ttc), 0))
        .filter(Facture.est_supprime.is_(False), Facture.date_facture >= prev_start, Facture.date_facture < prev_end)
        .scalar()
    )

    depenses_mois = (
        db.session.query(func.coalesce(func.sum(Depense.montant), 0))
        .filter(Depense.est_supprime.is_(False), Depense.date_depense >= now_start, Depense.date_depense < now_end)
        .scalar()
    )
    depenses_mois_prec = (
        db.session.query(func.coalesce(func.sum(Depense.montant), 0))
        .filter(Depense.est_supprime.is_(False), Depense.date_depense >= prev_start, Depense.date_depense < prev_end)
        .scalar()
    )

    nb_commandes_mois = Commande.query.filter(
        Commande.est_supprime.is_(False), Commande.date_commande >= now_start, Commande.date_commande < now_end
    ).count()
    nb_commandes_mois_prec = Commande.query.filter(
        Commande.est_supprime.is_(False), Commande.date_commande >= prev_start, Commande.date_commande < prev_end
    ).count()

    nb_clients = Client.query.filter_by(est_supprime=False).count()
    # La table `client` n'a pas de date de création (schéma d'origine).
    # On utilise la date de création du compte utilisateur lié comme proxy
    # honnête pour "nouveaux clients ce mois" (chaque inscription au portail
    # crée un compte + une fiche client).
    nouveaux_clients_mois = Utilisateur.query.filter(
        Utilisateur.created_at >= now_start, Utilisateur.created_at < now_end
    ).count()

    nb_factures_payees = Facture.query.filter_by(est_supprime=False, est_solder=True).count()
    nb_factures_impayees = Facture.query.filter_by(est_supprime=False, est_solder=False).count()

    nb_articles = Article.query.filter_by(est_supprime=False).count()

    factures_achats_mois = (
        db.session.query(func.coalesce(func.sum(FactureAchat.montant_ttc), 0))
        .filter(FactureAchat.est_supprime.is_(False), FactureAchat.date_facture >= now_start, FactureAchat.date_facture < now_end)
        .scalar()
    )

    marge_brute_mois = float(ca_mois) - float(factures_achats_mois)
    marge_nette_mois = marge_brute_mois - float(depenses_mois)

    tresorerie = (
        db.session.query(func.coalesce(func.sum(CompteBancaire.solde), 0))
        .filter(CompteBancaire.est_supprime.is_(False))
        .scalar()
    )

    kpis = {
        "chiffre_affaires": {"valeur": float(ca_mois), "variation": _variation(float(ca_mois), float(ca_mois_prec))},
        "nb_commandes": {"valeur": nb_commandes_mois, "variation": _variation(nb_commandes_mois, nb_commandes_mois_prec)},
        "nb_clients": {"valeur": nb_clients, "variation": None},
        "nouveaux_clients": {"valeur": nouveaux_clients_mois, "variation": None},
        "factures_payees": {"valeur": nb_factures_payees, "variation": None},
        "factures_impayees": {"valeur": nb_factures_impayees, "variation": None},
        "depenses": {"valeur": float(depenses_mois), "variation": _variation(float(depenses_mois), float(depenses_mois_prec))},
        "tresorerie": {"valeur": float(tresorerie), "variation": None},
        "marge_brute": {"valeur": marge_brute_mois, "variation": None},
        "marge_nette": {"valeur": marge_nette_mois, "variation": None},
        "nb_articles": {"valeur": nb_articles, "variation": None},
    }

    # ------------------------------------------------------------
    # Séries mensuelles (6 derniers mois) pour les graphiques
    # ------------------------------------------------------------
    series_ca = []
    series_depenses = []
    series_benefice = []
    labels = []
    for i in range(5, -1, -1):
        start, end = _month_bounds(i)
        ca = (
            db.session.query(func.coalesce(func.sum(Facture.total_ttc), 0))
            .filter(Facture.est_supprime.is_(False), Facture.date_facture >= start, Facture.date_facture < end)
            .scalar()
        )
        dep = (
            db.session.query(func.coalesce(func.sum(Depense.montant), 0))
            .filter(Depense.est_supprime.is_(False), Depense.date_depense >= start, Depense.date_depense < end)
            .scalar()
        )
        labels.append(month_name[start.month][:3])
        series_ca.append(float(ca))
        series_depenses.append(float(dep))
        series_benefice.append(float(ca) - float(dep))

    charts = {
        "labels": labels,
        "chiffre_affaires_mensuel": series_ca,
        "depenses_mensuel": series_depenses,
        "benefice_mensuel": series_benefice,
    }

    # ------------------------------------------------------------
    # Meilleurs clients (par total facturé)
    # ------------------------------------------------------------
    top_clients_rows = (
        db.session.query(Client.id, Client.nom, func.coalesce(func.sum(Facture.total_ttc), 0).label("total"))
        .join(Facture, Facture.client_id == Client.id)
        .filter(Facture.est_supprime.is_(False), Client.est_supprime.is_(False))
        .group_by(Client.id, Client.nom)
        .order_by(func.sum(Facture.total_ttc).desc())
        .limit(5)
        .all()
    )
    top_clients = [{"id": r.id, "nom": r.nom, "total": float(r.total)} for r in top_clients_rows]

    # ------------------------------------------------------------
    # Articles les plus vendus (par quantité, sur les factures)
    # ------------------------------------------------------------
    top_articles_rows = (
        db.session.query(
            ArticleFacture.nom_article,
            func.coalesce(func.sum(ArticleFacture.quantite), 0).label("quantite"),
            func.coalesce(func.sum(ArticleFacture.total_prix_ttc), 0).label("montant"),
        )
        .filter(ArticleFacture.est_supprime.is_(False))
        .group_by(ArticleFacture.nom_article)
        .order_by(func.sum(ArticleFacture.quantite).desc())
        .limit(5)
        .all()
    )
    top_articles = [
        {"nom": r.nom_article, "quantite": float(r.quantite), "montant": float(r.montant)}
        for r in top_articles_rows
    ]

    # ------------------------------------------------------------
    # Dernières factures / commandes (toutes, vue globale entreprise)
    # ------------------------------------------------------------
    dernieres_factures = (
        Facture.query.filter_by(est_supprime=False).order_by(Facture.date_facture.desc()).limit(5).all()
    )
    dernieres_commandes = (
        Commande.query.filter_by(est_supprime=False).order_by(Commande.date_commande.desc()).limit(5).all()
    )

    return jsonify(
        {
            "kpis": kpis,
            "charts": charts,
            "top_clients": top_clients,
            "top_articles": top_articles,
            "dernieres_factures": [f.to_dict() for f in dernieres_factures],
            "dernieres_commandes": [c.to_dict() for c in dernieres_commandes],
            "currency": "TND",
        }
    )
