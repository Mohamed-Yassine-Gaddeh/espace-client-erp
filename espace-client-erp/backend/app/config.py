import os
from datetime import timedelta


class Config:
    # --- Général ---
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-prod")

    # --- Base de données ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///espace_client.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- JWT ---
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "change-me-too")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    JWT_TOKEN_LOCATION = ["headers"]

    # --- CORS (adresse du frontend Angular) ---
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:4200").split(",")

    # --- ERP (à adapter à votre ERP réel) ---
    ERP_BASE_URL = os.environ.get("ERP_BASE_URL", "https://votre-erp.example.com/api")
    ERP_API_KEY = os.environ.get("ERP_API_KEY", "")
    ERP_TIMEOUT_SECONDS = int(os.environ.get("ERP_TIMEOUT_SECONDS", "10"))

    # --- Email (reset mot de passe) ---
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "no-reply@example.com")

    FRONTEND_RESET_URL = os.environ.get(
        "FRONTEND_RESET_URL", "http://localhost:4200/reset-password"
    )

    # --- Chatbot (optionnel) ---
    # Si ANTHROPIC_API_KEY est renseignée, le chatbot utilise Claude pour
    # reformuler des réponses naturelles à partir des données du client.
    # Sinon, il répond avec des réponses générées directement depuis la base
    # (aucune clé API n'est requise pour que le chatbot fonctionne).
    ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
