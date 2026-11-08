# Espace Client ERP — Authentification + Tableau de bord (schéma ERP intégré)

Backend Flask connecté **directement aux tables ERP réelles** (`client`,
`utilisateur`, `commande`, `facture`, `document`, `notification`, etc.) —
plus de couche HTTP intermédiaire vers un ERP distant : le portail lit et
écrit désormais dans les mêmes tables que votre ERP.

## Structure

```
espace-client-erp/
├── backend/
│   ├── app/
│   │   ├── auth/            # register, login, logout, reset password...
│   │   ├── dashboard/       # agrégation du tableau de bord (4.2)
│   │   ├── erp/             # client HTTP ERP (conservé, non utilisé par défaut)
│   │   ├── utils/           # envoi d'email
│   │   ├── models.py        # ancien modèle User/Notification (non utilisé désormais)
│   │   ├── models_erp.py    # ★ les 24 tables du schéma ERP + portail
│   │   ├── config.py
│   │   └── extensions.py
│   ├── requirements.txt
│   ├── .env.example
│   └── run.py
└── frontend/                # Angular 20 (standalone)
    └── src/app/
        ├── core/auth/
        └── features/
            ├── auth/
            └── dashboard/
```

## Ce qui a changé (intégration du schéma ERP)

- **`app/models_erp.py`** définit les 24 tables (16 ERP + 8 portail) exactement
  comme spécifié : `client`, `utilisateur`, `adresse`, `article`,
  `famille_article`, `sous_famille_article`, `tva`, `commande`,
  `article_commande`, `facture`, `article_facture`, `bon_livraison`,
  `article_bon_livraison`, `reglement`, `detail_reglement`, `document`,
  `panier`, `article_panier`, `historique_statut_commande`, `ticket`,
  `message_ticket`, `notification`, `piece_jointe`, `journal_audit`.

- **L'authentification utilise désormais `Utilisateur` + `Client`** (au lieu
  de l'ancien modèle `User`). À l'inscription :
  1. Recherche d'un `Client` existant avec le même email (rattachement).
  2. Sinon, création d'un nouveau `Client`.
  3. Création de l'`Utilisateur` lié à ce `Client` (`client_id`).

- **Le tableau de bord lit directement les tables locales** (`commande`,
  `facture`, `document`, `notification`) filtrées par `client_id` — plus
  d'appel réseau vers un ERP externe pour ces données.

- Testé de bout en bout (inscription → connexion → `/me` → dashboard →
  gestion des erreurs) avant livraison — voir section Tests plus bas.

## Démarrage — Backend

```bash
cd backend
python -m venv venv
source venv/Scripts/activate     # Windows Git Bash
# venv\Scripts\activate          # Windows cmd
# source venv/bin/activate       # Mac/Linux
pip install -r requirements.txt
cp .env.example .env             # copy .env.example .env  (Windows cmd)
python run.py
```

Toutes les tables sont créées automatiquement (`db.create_all()`) dans
`backend/instance/espace_client.db` au premier lancement.

## Démarrage — Frontend

```bash
cd frontend
npm install
npm start
```

Ouvrez `http://localhost:4200`.

## Endpoints disponibles

| Méthode | Endpoint                                   | Description                          |
|---------|----------------------------------------------|---------------------------------------|
| POST    | `/api/auth/register`                          | Création de compte (Client + Utilisateur) |
| POST    | `/api/auth/login`                             | Connexion                             |
| POST    | `/api/auth/logout`                            | Déconnexion (JWT requis)              |
| POST    | `/api/auth/refresh`                           | Renouvellement du token d'accès       |
| POST    | `/api/auth/forgot-password`                   | Demande de reset par email            |
| POST    | `/api/auth/reset-password`                    | Finalisation du reset                 |
| POST    | `/api/auth/change-password`                   | Changement de mdp (JWT requis)        |
| GET     | `/api/auth/me`                                | Profil (Utilisateur + Client lié)     |
| GET     | `/api/dashboard/summary`                      | Résumé du tableau de bord             |
| POST    | `/api/dashboard/notifications/<id>/read`      | Marquer une notification comme lue    |

## Points restant à clarifier avec vous

- Colonnes en attente de tables annexes non détaillées : `famille_id`,
  `mode_reglement_id` (client), `ville_id` (adresse), `unite_id` (article),
  `status_id` (commande/facture), `mode_livraison_id` (bon_livraison),
  `type_paiement_id` (reglement). Actuellement stockées en entier simple,
  sans contrainte de clé étrangère stricte.
- Le champ `roles` de `utilisateur` est une simple chaîne (ex. `"client"`).
  À adapter si vous voulez une gestion de rôles multiples plus formelle
  (table de jonction dédiée).
- L'ancien `app/models.py` (modèle `User`) n'est plus utilisé mais reste
  présent dans le projet ; à supprimer si vous confirmez ne plus en avoir besoin.

## Sécurité déjà en place

- Mots de passe hashés avec bcrypt (stockés dans `utilisateur.password`)
- JWT (access 30 min / refresh 7 jours) avec révocation à la déconnexion
- Validation stricte des mots de passe et des emails
- CORS restreint à `http://localhost:4200`
- `forgot-password` ne révèle jamais si un email existe ou non

## Nouveautés — Commandes, Factures, Notifications, Export PDF

- **Page Commandes** (`/orders`) : liste + détail avec lignes d'articles et
  **historique complet des changements de statut** (table `historique_statut_commande`).
- **Page Factures** (`/invoices`) : liste + détail avec lignes d'articles.
- **Page Notifications** (`/notifications`) : liste complète, marquage individuel
  ou global ("tout marquer comme lu").
- **Export PDF** : bouton "Télécharger le PDF" sur chaque commande et facture
  (génération à la volée via `reportlab`, voir `backend/app/utils/pdf_export.py`).
- Nouvelle **barre de navigation partagée** (`shared/nav-bar.component.ts`)
  entre Tableau de bord / Commandes / Factures / Notifications.

### Nouveaux endpoints

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/api/orders` | Liste des commandes du client |
| GET | `/api/orders/<id>` | Détail + historique des statuts |
| GET | `/api/orders/<id>/pdf` | Export PDF du bon de commande |
| GET | `/api/invoices` | Liste des factures du client |
| GET | `/api/invoices/<id>` | Détail d'une facture |
| GET | `/api/invoices/<id>/pdf` | Export PDF de la facture |
| GET | `/api/notifications` | Liste complète des notifications |
| POST | `/api/notifications/<id>/read` | Marquer une notification comme lue |
| POST | `/api/notifications/read-all` | Tout marquer comme lu |

### Note sur "gérer le statut des commandes"

Le statut d'une commande est normalement mis à jour côté ERP (par un
gestionnaire), pas par le client lui-même. J'ai donc implémenté la
**consultation** du statut actuel et de son historique complet — si vous
souhaitez que le client puisse déclencher une action (ex. demande d'annulation),
dites-le-moi et je l'ajoute.

### Nouvelle dépendance

`reportlab==4.2.5` a été ajoutée à `requirements.txt` (génération de PDF).
Pensez à relancer `pip install -r requirements.txt`.

### Tests effectués avant livraison

Backend lancé réellement (pas seulement en test interne), requêtes HTTP
envoyées avec un `Origin` simulant le navigateur, PDF générés et vérifiés
(en-tête `%PDF` présent), frontend compilé avec `ng build` sans erreur.

## Internationalisation (FR/EN)

- Langue par défaut : **français**. Sélecteur FR/EN dans la barre du haut, à côté de l'icône notifications et de l'avatar.
- Système basé sur un service Angular (`core/i18n/i18n.service.ts`) réactif via signals — changement de langue instantané, sans rechargement de page.
- Préférence de langue mémorisée dans le navigateur (`localStorage`), conservée d'une session à l'autre.
- Toutes les pages sont traduites : connexion, inscription, mot de passe oublié, tableau de bord, commandes, factures, clients, articles, notifications, modules "à venir", chatbot.
- Dictionnaire centralisé dans `core/i18n/translations.ts` — pour ajouter une langue ou un texte, c'est le seul fichier à modifier.
- Limite connue : les messages d'erreur renvoyés directement par le backend (validation de formulaire, ex. "Le nom est requis") restent en français, le backend n'étant pas encore internationalisé. Les messages générés côté frontend (réseau, connexion au serveur) sont traduits.

## Icône de notifications (remise dans la barre du haut)

Cloche 🔔 avec badge de compteur, à côté du sélecteur de langue et de l'avatar — mène à la page Notifications complète.
