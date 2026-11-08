from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models_erp import Utilisateur
from app.chatbot.service import build_context_and_answer
from app.chatbot.llm import refine_answer

chatbot_bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")


@chatbot_bp.post("/message")
@jwt_required()
def message():
    """
    Le client pose une question en langage naturel. On répond exclusivement
    à partir de ses propres données (jamais celles d'un autre client).
    """
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"errors": {"message": "Le message ne peut pas être vide."}}), 422

    if len(user_message) > 1000:
        return jsonify({"errors": {"message": "Message trop long (1000 caractères max)."}}), 422

    utilisateur = Utilisateur.query.get(int(get_jwt_identity()))
    if not utilisateur:
        return jsonify({"errors": {"general": "Utilisateur introuvable."}}), 404

    template_answer, used_data = build_context_and_answer(utilisateur, user_message)

    try:
        final_answer = refine_answer(user_message, template_answer, used_data)
    except Exception as exc:  # ne doit jamais faire planter le chat
        current_app.logger.warning("Chatbot : reformulation échouée (%s)", exc)
        final_answer = template_answer

    return jsonify({"answer": final_answer})
