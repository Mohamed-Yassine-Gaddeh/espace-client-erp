from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models_erp import Article, FamilleArticle, SousFamilleArticle, Tva

articles_bp = Blueprint("articles_mgmt", __name__, url_prefix="/api/articles")


def _article_to_dict(a: Article) -> dict:
    return {
        "id": a.id,
        "nom": a.nom,
        "reference": a.reference,
        "description": a.description,
        "prix_vente_ht": float(a.prix_vente_ht) if a.prix_vente_ht is not None else 0,
        "prix_vente_ttc": float(a.prix_vente_ttc) if a.prix_vente_ttc is not None else 0,
        "est_service": a.est_service,
        "est_bloque": a.est_bloque,
        "stock_disponible": float(a.stock_disponible) if a.stock_disponible is not None else 0,
        "tva_id": a.tva_id,
        "famille_article_id": a.famille_article_id,
        "sous_famille_article_id": a.sous_famille_article_id,
        "famille_libelle": a.famille_article.libelle if a.famille_article else None,
        "tva_valeur": float(a.tva.valeur) if a.tva else None,
    }


@articles_bp.get("")
@jwt_required()
def list_articles():
    articles = Article.query.filter_by(est_supprime=False).order_by(Article.nom.asc()).all()
    return jsonify({"articles": [_article_to_dict(a) for a in articles]})


@articles_bp.get("/<int:article_id>")
@jwt_required()
def get_article(article_id: int):
    article = Article.query.filter_by(id=article_id, est_supprime=False).first()
    if not article:
        return jsonify({"errors": {"general": "Article introuvable."}}), 404
    return jsonify({"article": _article_to_dict(article)})


@articles_bp.get("/options/familles")
@jwt_required()
def list_familles():
    """Pour les listes déroulantes du formulaire (famille + TVA)."""
    familles = FamilleArticle.query.filter_by(est_desactive=False).order_by(FamilleArticle.libelle).all()
    tvas = Tva.query.filter_by(est_supprime=False).order_by(Tva.valeur).all()
    return jsonify(
        {
            "familles": [{"id": f.id, "libelle": f.libelle} for f in familles],
            "tvas": [{"id": t.id, "libelle": t.libelle, "valeur": float(t.valeur)} for t in tvas],
        }
    )


@articles_bp.post("")
@jwt_required()
def create_article():
    data = request.get_json(silent=True) or {}
    nom = (data.get("nom") or "").strip()
    if not nom:
        return jsonify({"errors": {"nom": "Le nom est requis."}}), 422

    try:
        prix_ht = float(data.get("prix_vente_ht") or 0)
        prix_ttc = float(data.get("prix_vente_ttc") or 0)
        stock = float(data.get("stock_disponible") or 0)
    except (TypeError, ValueError):
        return jsonify({"errors": {"prix_vente_ht": "Valeur numérique invalide."}}), 422

    article = Article(
        nom=nom,
        reference=(data.get("reference") or "").strip() or None,
        description=(data.get("description") or "").strip() or None,
        prix_vente_ht=prix_ht,
        prix_vente_ttc=prix_ttc,
        stock_disponible=stock,
        est_service=bool(data.get("est_service", False)),
        tva_id=data.get("tva_id") or None,
        famille_article_id=data.get("famille_article_id") or None,
        sous_famille_article_id=data.get("sous_famille_article_id") or None,
    )
    db.session.add(article)
    db.session.commit()
    return jsonify({"article": _article_to_dict(article)}), 201


@articles_bp.put("/<int:article_id>")
@jwt_required()
def update_article(article_id: int):
    article = Article.query.filter_by(id=article_id, est_supprime=False).first()
    if not article:
        return jsonify({"errors": {"general": "Article introuvable."}}), 404

    data = request.get_json(silent=True) or {}

    if "nom" in data:
        nom = (data.get("nom") or "").strip()
        if not nom:
            return jsonify({"errors": {"nom": "Le nom est requis."}}), 422
        article.nom = nom

    for field in ["reference", "description"]:
        if field in data:
            setattr(article, field, (data.get(field) or "").strip() or None)

    for field in ["prix_vente_ht", "prix_vente_ttc", "stock_disponible"]:
        if field in data:
            try:
                setattr(article, field, float(data.get(field) or 0))
            except (TypeError, ValueError):
                return jsonify({"errors": {field: "Valeur numérique invalide."}}), 422

    if "est_service" in data:
        article.est_service = bool(data.get("est_service"))
    if "est_bloque" in data:
        article.est_bloque = bool(data.get("est_bloque"))
    if "tva_id" in data:
        article.tva_id = data.get("tva_id") or None
    if "famille_article_id" in data:
        article.famille_article_id = data.get("famille_article_id") or None
    if "sous_famille_article_id" in data:
        article.sous_famille_article_id = data.get("sous_famille_article_id") or None

    db.session.commit()
    return jsonify({"article": _article_to_dict(article)})


@articles_bp.delete("/<int:article_id>")
@jwt_required()
def delete_article(article_id: int):
    """Suppression logique (est_supprime=True), jamais de suppression physique."""
    article = Article.query.filter_by(id=article_id, est_supprime=False).first()
    if not article:
        return jsonify({"errors": {"general": "Article introuvable."}}), 404

    article.est_supprime = True
    db.session.commit()
    return jsonify({"message": "Article supprimé."})
