"""
Client d'intégration ERP.

Ce module centralise tous les appels vers l'ERP. À ce stade, seules les
méthodes nécessaires à l'authentification sont implémentées (retrouver /
créer la fiche client correspondant au compte portail).

IMPORTANT : adaptez `_headers()`, les URLs et le format des payloads/réponses
aux spécifications réelles de votre API ERP (auth par API key, OAuth2,
format des champs, etc.).
"""

import requests
from flask import current_app


class ErpClientError(Exception):
    """Erreur générique lors d'un appel à l'ERP."""


class ErpClient:
    def _base_url(self) -> str:
        return current_app.config["ERP_BASE_URL"].rstrip("/")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {current_app.config['ERP_API_KEY']}",
            "Content-Type": "application/json",
        }

    def _timeout(self) -> int:
        return current_app.config["ERP_TIMEOUT_SECONDS"]

    def find_customer_by_email(self, email: str) -> dict | None:
        """Recherche une fiche client existante dans l'ERP par email."""
        try:
            resp = requests.get(
                f"{self._base_url()}/customers",
                params={"email": email},
                headers=self._headers(),
                timeout=self._timeout(),
            )
            resp.raise_for_status()
            results = resp.json().get("data", [])
            return results[0] if results else None
        except requests.RequestException as exc:
            current_app.logger.error("Erreur ERP (find_customer_by_email): %s", exc)
            raise ErpClientError("Impossible de contacter l'ERP.") from exc

    def create_customer(self, first_name: str, last_name: str, email: str, phone: str | None) -> dict:
        """Crée une fiche client dans l'ERP lors d'une inscription portail."""
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": phone,
            "source": "espace_client_portal",
        }
        try:
            resp = requests.post(
                f"{self._base_url()}/customers",
                json=payload,
                headers=self._headers(),
                timeout=self._timeout(),
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            current_app.logger.error("Erreur ERP (create_customer): %s", exc)
            raise ErpClientError("Impossible de créer la fiche client dans l'ERP.") from exc

    # ------------------------------------------------------------------
    # Méthodes utilisées par le tableau de bord (module 4.2)
    # Adaptez les URLs / la forme des réponses aux endpoints réels de
    # votre ERP. Chaque méthode retourne une structure déjà normalisée
    # pour le frontend, afin que le reste de l'application n'ait pas à
    # connaître le format brut de l'ERP.
    # ------------------------------------------------------------------

    def get_account_balance(self, customer_id: str) -> dict:
        """4.2 Solde du compte."""
        try:
            resp = requests.get(
                f"{self._base_url()}/customers/{customer_id}/balance",
                headers=self._headers(),
                timeout=self._timeout(),
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "balance": data.get("balance", 0),
                "currency": data.get("currency", "TND"),
            }
        except requests.RequestException as exc:
            current_app.logger.error("Erreur ERP (get_account_balance): %s", exc)
            raise ErpClientError("Impossible de récupérer le solde du compte.") from exc

    def get_recent_orders(self, customer_id: str, limit: int = 5) -> list[dict]:
        """4.2 Dernières commandes."""
        try:
            resp = requests.get(
                f"{self._base_url()}/customers/{customer_id}/orders",
                params={"limit": limit, "sort": "-date"},
                headers=self._headers(),
                timeout=self._timeout(),
            )
            resp.raise_for_status()
            orders = resp.json().get("data", [])
            return [
                {
                    "id": o.get("id"),
                    "reference": o.get("reference"),
                    "date": o.get("date"),
                    "status": o.get("status"),
                    "total": o.get("total"),
                }
                for o in orders
            ]
        except requests.RequestException as exc:
            current_app.logger.error("Erreur ERP (get_recent_orders): %s", exc)
            raise ErpClientError("Impossible de récupérer les commandes.") from exc

    def get_recent_invoices(self, customer_id: str, limit: int = 5) -> list[dict]:
        """4.2 Dernières factures."""
        try:
            resp = requests.get(
                f"{self._base_url()}/customers/{customer_id}/invoices",
                params={"limit": limit, "sort": "-date"},
                headers=self._headers(),
                timeout=self._timeout(),
            )
            resp.raise_for_status()
            invoices = resp.json().get("data", [])
            return [
                {
                    "id": i.get("id"),
                    "number": i.get("number"),
                    "date": i.get("date"),
                    "due_date": i.get("due_date"),
                    "amount": i.get("amount"),
                    "payment_status": i.get("payment_status"),
                }
                for i in invoices
            ]
        except requests.RequestException as exc:
            current_app.logger.error("Erreur ERP (get_recent_invoices): %s", exc)
            raise ErpClientError("Impossible de récupérer les factures.") from exc

    def get_recent_documents(self, customer_id: str, limit: int = 5) -> list[dict]:
        """4.2 Documents récents (tous types confondus)."""
        try:
            resp = requests.get(
                f"{self._base_url()}/customers/{customer_id}/documents",
                params={"limit": limit, "sort": "-date"},
                headers=self._headers(),
                timeout=self._timeout(),
            )
            resp.raise_for_status()
            docs = resp.json().get("data", [])
            return [
                {
                    "id": d.get("id"),
                    "type": d.get("type"),  # facture, devis, bon_commande, ...
                    "name": d.get("name"),
                    "date": d.get("date"),
                    "download_url": d.get("download_url"),
                }
                for d in docs
            ]
        except requests.RequestException as exc:
            current_app.logger.error("Erreur ERP (get_recent_documents): %s", exc)
            raise ErpClientError("Impossible de récupérer les documents.") from exc

    def get_order_status_summary(self, customer_id: str) -> dict:
        """4.2 Statut des commandes (répartition par statut)."""
        try:
            resp = requests.get(
                f"{self._base_url()}/customers/{customer_id}/orders/status-summary",
                headers=self._headers(),
                timeout=self._timeout(),
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            current_app.logger.error("Erreur ERP (get_order_status_summary): %s", exc)
            raise ErpClientError("Impossible de récupérer le statut des commandes.") from exc


erp_client = ErpClient()
