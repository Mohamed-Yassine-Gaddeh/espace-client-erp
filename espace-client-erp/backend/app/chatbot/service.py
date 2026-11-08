"""
Chatbot du portail client.

Principe :
1. On détecte l'intention du message par mots-clés (français).
2. On va chercher les données correspondantes dans la base (uniquement
   celles du client connecté — jamais celles d'un autre client).
3. On formule une réponse :
   - si ANTHROPIC_API_KEY est configurée, on demande à Claude de reformuler
     une réponse naturelle à partir des données récupérées (jamais l'inverse :
     le modèle ne reçoit que les données déjà filtrées pour ce client) ;
   - sinon, on renvoie une réponse générée directement depuis un gabarit,
     sans dépendance à une clé API.
"""

from app.models_erp import Commande, Facture, Document, NotificationErp, Utilisateur


def _fmt_montant(valeur) -> str:
    try:
        return f"{float(valeur):.2f}"
    except (TypeError, ValueError):
        return "0.00"


def detect_intent(message: str) -> str:
    m = message.lower()

    if any(k in m for k in ["solde", "je dois", "montant du", "combien je dois", "reste à payer"]):
        return "solde"
    if any(k in m for k in ["commande", "commandes"]):
        return "commandes"
    if any(k in m for k in ["facture", "factures"]):
        return "factures"
    if any(k in m for k in ["document", "documents", "télécharger"]):
        return "documents"
    if any(k in m for k in ["notification", "notifications"]):
        return "notifications"
    if any(k in m for k in ["mon compte", "mes informations", "profil", "coordonnées"]):
        return "profil"
    if any(k in m for k in ["bonjour", "salut", "bonsoir", "hello"]):
        return "salutation"
    if any(k in m for k in ["merci"]):
        return "remerciement"
    return "inconnu"


def build_context_and_answer(utilisateur: Utilisateur, message: str) -> tuple[str, dict]:
    """
    Retourne (réponse_texte, données_utilisées).
    `données_utilisées` sert de contexte pour l'éventuel appel à Claude, et
    peut aussi être affiché tel quel côté frontend si besoin de débogage.
    """
    intent = detect_intent(message)
    client = utilisateur.client

    if intent == "salutation":
        return (
            f"Bonjour {utilisateur.nom} 👋 Je peux vous renseigner sur votre solde, "
            "vos commandes, vos factures, vos documents ou vos notifications. "
            "Que souhaitez-vous savoir ?",
            {},
        )

    if intent == "remerciement":
        return ("Avec plaisir ! N'hésitez pas si vous avez d'autres questions.", {})

    if not client:
        return (
            "Votre compte n'est pas encore relié à une fiche client, je ne peux "
            "donc pas encore accéder à vos données. Contactez le support pour "
            "finaliser le rattachement.",
            {},
        )

    if intent == "solde":
        factures_non_soldees = Facture.query.filter_by(
            client_id=client.id, est_supprime=False, est_solder=False
        ).all()
        solde_total = sum((f.solde_du or 0) for f in factures_non_soldees)
        data = {"solde_du": float(solde_total), "nb_factures_impayees": len(factures_non_soldees)}
        if solde_total > 0:
            texte = (
                f"Votre solde restant dû est de {_fmt_montant(solde_total)} TND, "
                f"réparti sur {len(factures_non_soldees)} facture(s) non soldée(s)."
            )
        else:
            texte = "Vous n'avez aucun solde restant dû. Votre compte est à jour."
        return texte, data

    if intent == "commandes":
        commandes = (
            Commande.query.filter_by(client_id=client.id, est_supprime=False)
            .order_by(Commande.date_commande.desc())
            .limit(5)
            .all()
        )
        data = {"commandes": [c.to_dict() for c in commandes]}
        if not commandes:
            return "Vous n'avez aucune commande enregistrée pour le moment.", data
        lignes = [
            f"- {c.numero} du {c.date_commande.strftime('%d/%m/%Y') if c.date_commande else '?'} "
            f"— {_fmt_montant(c.total_ttc)} TND"
            for c in commandes
        ]
        texte = "Voici vos " + str(len(commandes)) + " dernière(s) commande(s) :\n" + "\n".join(lignes)
        return texte, data

    if intent == "factures":
        factures = (
            Facture.query.filter_by(client_id=client.id, est_supprime=False)
            .order_by(Facture.date_facture.desc())
            .limit(5)
            .all()
        )
        data = {"factures": [f.to_dict() for f in factures]}
        if not factures:
            return "Vous n'avez aucune facture enregistrée pour le moment.", data
        lignes = [
            f"- {f.numero} du {f.date_facture.strftime('%d/%m/%Y') if f.date_facture else '?'} "
            f"— {_fmt_montant(f.total_ttc)} TND ({'soldée' if f.est_solder else 'en attente'})"
            for f in factures
        ]
        texte = "Voici vos " + str(len(factures)) + " dernière(s) facture(s) :\n" + "\n".join(lignes)
        return texte, data

    if intent == "documents":
        documents = (
            Document.query.filter_by(client_id=client.id, est_supprime=False)
            .order_by(Document.id.desc())
            .limit(5)
            .all()
        )
        data = {"documents": [{"nom": d.nom, "lien": d.lien} for d in documents]}
        if not documents:
            return "Aucun document n'est disponible pour votre compte pour le moment.", data
        lignes = [f"- {d.nom}" for d in documents]
        texte = "Voici vos documents récents :\n" + "\n".join(lignes)
        return texte, data

    if intent == "notifications":
        notifications = (
            NotificationErp.query.filter_by(utilisateur_id=utilisateur.id)
            .order_by(NotificationErp.created_at.desc())
            .limit(5)
            .all()
        )
        data = {"notifications": [{"titre": n.titre, "lu": n.est_lu} for n in notifications]}
        if not notifications:
            return "Vous n'avez aucune notification pour le moment.", data
        lignes = [f"- {'✓' if n.est_lu else '●'} {n.titre}" for n in notifications]
        texte = "Voici vos dernières notifications :\n" + "\n".join(lignes)
        return texte, data

    if intent == "profil":
        data = {"client": client.to_dict()}
        texte = (
            f"Voici vos informations : \n"
            f"- Nom : {client.nom}\n"
            f"- Email : {client.email or 'non renseigné'}\n"
            f"- Téléphone : {client.telephone or 'non renseigné'}\n"
            "Pour modifier ces informations, rendez-vous dans votre profil."
        )
        return texte, data

    return (
        "Je peux vous renseigner sur : votre solde, vos commandes, vos factures, "
        "vos documents, vos notifications ou votre profil. Pouvez-vous reformuler "
        "votre question avec l'un de ces sujets ?",
        {},
    )
