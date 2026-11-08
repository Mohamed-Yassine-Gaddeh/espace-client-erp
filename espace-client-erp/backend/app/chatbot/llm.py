"""
Reformulation optionnelle des réponses du chatbot via l'API Anthropic.

Si aucune clé n'est configurée (ANTHROPIC_API_KEY vide), on n'appelle pas
l'API : la réponse générée depuis le gabarit (voir service.py) est utilisée
telle quelle. Le chatbot fonctionne donc sans dépendance externe.
"""

import requests
from flask import current_app


ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


def refine_answer(user_message: str, template_answer: str, data: dict) -> str:
    api_key = current_app.config.get("ANTHROPIC_API_KEY")
    if not api_key:
        return template_answer

    system_prompt = (
        "Tu es l'assistant du portail client d'un ERP. Réponds UNIQUEMENT à "
        "partir des données fournies ci-dessous, en français, de façon brève, "
        "claire et professionnelle. N'invente aucune donnée. Si les données "
        "sont vides, dis-le simplement.\n\n"
        f"Données du client concerné :\n{data}\n\n"
        f"Réponse de référence à reformuler (ne pas dénaturer les chiffres) :\n"
        f"{template_answer}"
    )

    try:
        resp = requests.post(
            ANTHROPIC_API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": current_app.config.get("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"),
                "max_tokens": 300,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=15,
        )
        resp.raise_for_status()
        content = resp.json().get("content", [])
        texte = "".join(block.get("text", "") for block in content if block.get("type") == "text")
        return texte.strip() or template_answer
    except requests.RequestException as exc:
        current_app.logger.warning("Chatbot : appel Claude échoué, fallback gabarit (%s)", exc)
        return template_answer
