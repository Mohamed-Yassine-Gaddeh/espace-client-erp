from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models_erp import Client

clients_bp = Blueprint("clients", __name__, url_prefix="/api/clients")


@clients_bp.get("")
@jwt_required()
def list_clients():
    """Liste de toutes les fiches clients."""
    clients = Client.query.filter_by(est_supprime=False).order_by(Client.nom.asc()).all()
    return jsonify({"clients": [c.to_dict() for c in clients]})


@clients_bp.get("/<int:client_id>")
@jwt_required()
def get_client(client_id: int):
    client = Client.query.filter_by(id=client_id, est_supprime=False).first()
    if not client:
        return jsonify({"errors": {"general": "Client introuvable."}}), 404
    return jsonify({"client": client.to_dict()})


@clients_bp.post("")
@jwt_required()
def create_client():
    data = request.get_json(silent=True) or {}
    nom = (data.get("nom") or "").strip()
    if not nom:
        return jsonify({"errors": {"nom": "Le nom est requis."}}), 422

    client = Client(
        nom=nom,
        code=(data.get("code") or "").strip() or None,
        email=(data.get("email") or "").strip() or None,
        telephone=(data.get("telephone") or "").strip() or None,
        portable=(data.get("portable") or "").strip() or None,
        numero_tva=(data.get("numero_tva") or "").strip() or None,
        siret=(data.get("siret") or "").strip() or None,
        site_web=(data.get("site_web") or "").strip() or None,
    )
    db.session.add(client)
    db.session.commit()
    return jsonify({"client": client.to_dict()}), 201


@clients_bp.put("/<int:client_id>")
@jwt_required()
def update_client(client_id: int):
    client = Client.query.filter_by(id=client_id, est_supprime=False).first()
    if not client:
        return jsonify({"errors": {"general": "Client introuvable."}}), 404

    data = request.get_json(silent=True) or {}
    for field in [
        "nom",
        "code",
        "email",
        "telephone",
        "portable",
        "numero_tva",
        "siret",
        "site_web",
    ]:
        if field in data:
            value = (data.get(field) or "").strip() or None
            setattr(client, field, value)

    if "nom" in data and not client.nom:
        return jsonify({"errors": {"nom": "Le nom est requis."}}), 422

    db.session.commit()
    return jsonify({"client": client.to_dict()})
