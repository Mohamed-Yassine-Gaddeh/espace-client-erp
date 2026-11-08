from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message

from app.extensions import mail


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def generate_reset_token(utilisateur) -> str:
    payload = {
        "email": utilisateur.email,
        "pwd_ts": utilisateur.password_changed_at.isoformat()
        if utilisateur.password_changed_at
        else "",
    }
    return _serializer().dumps(payload, salt="password-reset")


def verify_reset_token(token: str, max_age_seconds: int = 3600) -> dict | None:
    """Retourne {'email': ..., 'pwd_ts': ...} si le token est syntaxiquement
    valide et pas expiré, ou None sinon. Ne vérifie PAS ici si le mot de passe
    a changé depuis — cette vérification se fait dans la route, contre la
    valeur actuelle en base (voir reset_password)."""
    try:
        return _serializer().loads(token, salt="password-reset", max_age=max_age_seconds)
    except Exception:
        return None


def is_smtp_configured() -> bool:
    """Vérifie si un vrai serveur SMTP est configuré (pas les valeurs par défaut)."""
    server = current_app.config.get("MAIL_SERVER", "")
    username = current_app.config.get("MAIL_USERNAME", "")
    password = current_app.config.get("MAIL_PASSWORD", "")
    return bool(server) and server != "smtp.example.com" and bool(username) and bool(password)


def build_reset_link(token: str) -> str:
    return f"{current_app.config['FRONTEND_RESET_URL']}?token={token}"


def send_password_reset_email(to_email: str, token: str) -> None:
    """
    Envoie l'email de reset si un SMTP réel est configuré.

    Si aucun SMTP n'est configuré (cas du développement local sans boîte
    mail à disposition), le lien est simplement affiché dans les logs du
    terminal backend, bien visible, pour permettre de tester le flux complet
    de bout en bout sans dépendre d'un service d'email externe.
    """
    reset_link = build_reset_link(token)

    if not is_smtp_configured():
        current_app.logger.warning(
            "\n"
            "==================== MODE DÉVELOPPEMENT — PAS DE SMTP CONFIGURÉ ====================\n"
            "Aucun serveur SMTP réel n'est configuré dans .env (MAIL_SERVER/MAIL_USERNAME/"
            "MAIL_PASSWORD). Aucun email n'a été envoyé.\n"
            f"Lien de réinitialisation pour {to_email} :\n{reset_link}\n"
            "Configurez un vrai SMTP dans backend/.env pour un envoi réel (voir .env.example).\n"
            "======================================================================================\n"
        )
        return

    msg = Message(
        subject="Réinitialisation de votre mot de passe",
        recipients=[to_email],
        body=(
            "Bonjour,\n\n"
            "Vous avez demandé la réinitialisation de votre mot de passe.\n"
            f"Cliquez sur ce lien pour choisir un nouveau mot de passe : {reset_link}\n\n"
            "Ce lien expire dans 1 heure. Si vous n'êtes pas à l'origine de cette "
            "demande, ignorez cet email.\n"
        ),
    )
    mail.send(msg)
