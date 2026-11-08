from datetime import datetime

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)

from app.extensions import db
from app.models_erp import Utilisateur, Client
from app.utils.email import (
    generate_reset_token,
    verify_reset_token,
    send_password_reset_email,
    is_smtp_configured,
    build_reset_link,
)
from app.auth.schemas import (
    validate_registration,
    validate_login,
    validate_password_change,
    ValidationErrors,
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# Liste noire simple des jti révoqués (à remplacer par Redis en production)
_revoked_tokens: set[str] = set()


def _get_current_utilisateur() -> Utilisateur | None:
    """get_jwt_identity() renvoie une chaîne (obligatoire côté JWT) ; on la reconvertit en int."""
    identity = get_jwt_identity()
    if identity is None:
        return None
    return Utilisateur.query.get(int(identity))


@auth_bp.post("/register")
def register():
    """4.1 Création de compte — crée la fiche client ERP et le compte utilisateur liés."""
    data = request.get_json(silent=True) or {}
    try:
        clean = validate_registration(data)
    except ValidationErrors as e:
        return jsonify({"errors": e.errors}), 422

    if Utilisateur.query.filter_by(email=clean["email"]).first():
        return jsonify({"errors": {"email": "Un compte existe déjà avec cet email."}}), 409

    nom_complet = f"{clean['first_name']} {clean['last_name']}".strip()

    # On rattache le compte à une fiche client existante (même email) si elle
    # existe déjà dans l'ERP, sinon on en crée une nouvelle.
    client = Client.query.filter_by(email=clean["email"]).first()
    if not client:
        client = Client(
            nom=nom_complet,
            email=clean["email"],
            telephone=clean["phone"],
        )
        db.session.add(client)
        db.session.flush()  # pour obtenir client.id avant de créer l'utilisateur

    utilisateur = Utilisateur(
        email=clean["email"],
        nom=nom_complet,
        roles="client",
        status="actif",
        client_id=client.id,
    )
    utilisateur.set_password(clean["password"])

    db.session.add(utilisateur)
    db.session.commit()

    access_token = create_access_token(
        identity=str(utilisateur.id), additional_claims={"roles": utilisateur.roles}
    )
    refresh_token = create_refresh_token(identity=str(utilisateur.id))

    return (
        jsonify(
            {
                "user": utilisateur.to_dict(),
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        ),
        201,
    )


@auth_bp.post("/login")
def login():
    """4.1 Connexion."""
    data = request.get_json(silent=True) or {}
    try:
        clean = validate_login(data)
    except ValidationErrors as e:
        return jsonify({"errors": e.errors}), 422

    utilisateur = Utilisateur.query.filter_by(email=clean["email"]).first()

    if not utilisateur or not utilisateur.check_password(clean["password"]):
        return jsonify({"errors": {"general": "Email ou mot de passe incorrect."}}), 401

    if utilisateur.est_bloque:
        return jsonify({"errors": {"general": "Ce compte a été bloqué."}}), 403

    if utilisateur.est_supprime:
        return jsonify({"errors": {"general": "Ce compte n'existe plus."}}), 403

    db.session.commit()

    access_token = create_access_token(
        identity=str(utilisateur.id), additional_claims={"roles": utilisateur.roles}
    )
    refresh_token = create_refresh_token(identity=str(utilisateur.id))

    return jsonify(
        {
            "user": utilisateur.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    """Renouvellement du token d'accès à partir du refresh token."""
    utilisateur = _get_current_utilisateur()
    if not utilisateur or utilisateur.est_bloque or utilisateur.est_supprime:
        return jsonify({"errors": {"general": "Compte introuvable ou désactivé."}}), 401

    access_token = create_access_token(
        identity=str(utilisateur.id), additional_claims={"roles": utilisateur.roles}
    )
    return jsonify({"access_token": access_token})


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """4.1 Déconnexion — révoque le token courant."""
    jti = get_jwt()["jti"]
    _revoked_tokens.add(jti)
    return jsonify({"message": "Déconnexion réussie."})


@auth_bp.post("/forgot-password")
def forgot_password():
    """4.1 Mot de passe oublié."""
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    utilisateur = Utilisateur.query.filter_by(email=email).first()
    # On répond toujours le même message, que l'email existe ou non,
    # pour ne pas révéler quels emails sont enregistrés.
    if utilisateur:
        token = generate_reset_token(utilisateur)
        try:
            send_password_reset_email(utilisateur.email, token)
        except Exception as e:
            current_app.logger.error("Échec envoi email de reset : %s", e)

    return jsonify({"message": "Un email de réinitialisation vient d'être envoyé."})


@auth_bp.post("/reset-password")
def reset_password():
    """Finalisation du reset de mot de passe via le token reçu par email."""
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    new_password = data.get("new_password") or ""

    payload = verify_reset_token(token, max_age_seconds=3600) if token else None
    if not payload or not payload.get("email"):
        return jsonify({"errors": {"token": "Lien invalide ou expiré."}}), 400

    email = payload["email"]

    from app.auth.schemas import PASSWORD_REGEX

    if not PASSWORD_REGEX.match(new_password):
        return jsonify(
            {
                "errors": {
                    "new_password": "Le mot de passe doit contenir au moins 8 caractères, "
                    "une majuscule, une minuscule, un chiffre et un caractère spécial."
                }
            }
        ), 422

    utilisateur = Utilisateur.query.filter_by(email=email).first()
    if not utilisateur:
        return jsonify({"errors": {"token": "Compte introuvable."}}), 404

    # Le lien ne peut servir qu'une fois : si le mot de passe a déjà été changé
    # depuis l'émission de ce token (reset précédent, ou changement manuel),
    # le token est considéré périmé même s'il n'a pas atteint sa durée de vie max.
    current_ts = utilisateur.password_changed_at.isoformat() if utilisateur.password_changed_at else ""
    if payload.get("pwd_ts", "") != current_ts:
        return jsonify({"errors": {"token": "Ce lien a déjà été utilisé ou n'est plus valide."}}), 400

    utilisateur.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Mot de passe réinitialisé avec succès."})


@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    """4.3 Changement de mot de passe (utilisateur connecté)."""
    data = request.get_json(silent=True) or {}
    try:
        clean = validate_password_change(data)
    except ValidationErrors as e:
        return jsonify({"errors": e.errors}), 422

    utilisateur = _get_current_utilisateur()
    if not utilisateur or not utilisateur.check_password(clean["current_password"]):
        return jsonify({"errors": {"current_password": "Mot de passe actuel incorrect."}}), 401

    utilisateur.set_password(clean["new_password"])
    db.session.commit()

    return jsonify({"message": "Mot de passe modifié avec succès."})


@auth_bp.get("/me")
@jwt_required()
def me():
    """Retourne le profil de l'utilisateur connecté (compte + fiche client liée)."""
    utilisateur = _get_current_utilisateur()
    if not utilisateur:
        return jsonify({"errors": {"general": "Utilisateur introuvable."}}), 404
    return jsonify({"user": utilisateur.to_dict()})


def is_token_revoked(jwt_header, jwt_payload) -> bool:
    return jwt_payload["jti"] in _revoked_tokens
