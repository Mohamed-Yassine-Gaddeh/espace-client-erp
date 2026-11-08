from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, jwt, bcrypt, cors, mail


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # --- Extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)

    # CORS : on autorise les origines explicitement configurées (CORS_ORIGINS)
    # ET, en développement, tout localhost/127.0.0.1 quel que soit le port.
    # Utile car `ng serve` bascule automatiquement sur un autre port (4201,
    # 4202...) si le port 4200 est déjà occupé, ce qui bloquerait silencieusement
    # les requêtes si on ne whitelistait qu'un seul port fixe.
    import re

    allowed_origins = list(app.config["CORS_ORIGINS"])
    if not app.config.get("FLASK_ENV") == "production":
        allowed_origins.append(re.compile(r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"))

    cors.init_app(app, resources={r"/api/*": {"origins": allowed_origins}})

    # --- Blueprints ---
    from app.auth.routes import auth_bp, is_token_revoked
    from app.dashboard.routes import dashboard_bp
    from app.dashboard.kpis_routes import dashboard_kpis_bp
    from app.chatbot.routes import chatbot_bp
    from app.orders.routes import orders_bp
    from app.invoices.routes import invoices_bp
    from app.notifications.routes import notifications_bp
    from app.clients_module.routes import clients_bp
    from app.articles_module.routes import articles_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dashboard_kpis_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(invoices_bp)
    app.register_blueprint(notifications_bp)  # API conservée, non liée dans l'UI
    app.register_blueprint(clients_bp)
    app.register_blueprint(articles_bp)

    # Import des modèles pour que SQLAlchemy les enregistre avant create_all()
    from app import models_erp  # noqa: F401  (import nécessaire, non utilisé directement ici)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return is_token_revoked(jwt_header, jwt_payload)

    # --- Gestion d'erreurs JWT propres (JSON, pas HTML) ---
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"errors": {"general": "Authentification requise."}}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"errors": {"general": "Token invalide."}}), 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"errors": {"general": "Le token a expiré."}}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"errors": {"general": "Ce token a été révoqué."}}), 401

    # --- Healthcheck ---
    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    with app.app_context():
        db.create_all()

    return app
