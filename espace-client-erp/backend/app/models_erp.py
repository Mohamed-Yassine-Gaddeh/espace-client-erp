"""
Modèles SQLAlchemy correspondant au schéma de base de données ERP fourni,
plus les tables spécifiques au portail client.

Convention respectée : noms de tables et de colonnes en français, identiques
à la structure communiquée, pour garantir la compatibilité avec l'ERP.

NOTE IMPORTANTE :
Certaines colonnes référencent des tables non détaillées dans le schéma
fourni (ex. `famille_id` et `mode_reglement_id` sur `client`, `ville_id` sur
`adresse`, `unite_id` sur `article`, `status_id` sur `commande`/`facture`,
`mode_livraison_id` sur `bon_livraison`, `type_paiement_id` sur `reglement`).
Ces colonnes sont créées en tant qu'entiers simples (pas de contrainte
ForeignKey stricte) pour ne pas bloquer la création des tables tant que ces
tables annexes ne sont pas définies. Ajoutez la contrainte ForeignKey dès que
vous me communiquez leur structure.
"""

from datetime import datetime
from app.extensions import db, bcrypt


# ============================================================
# 1. CLIENT
# ============================================================
class Client(db.Model):
    __tablename__ = "client"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=True, index=True)
    nom = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True, index=True)
    telephone = db.Column(db.String(30), nullable=True)
    portable = db.Column(db.String(30), nullable=True)
    numero_tva = db.Column(db.String(50), nullable=True)
    siret = db.Column(db.String(50), nullable=True)
    site_web = db.Column(db.String(255), nullable=True)
    est_bloquer = db.Column(db.Boolean, default=False, nullable=False)
    est_pospect = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    # Tables annexes non détaillées dans le schéma fourni
    famille_id = db.Column(db.Integer, nullable=True)
    mode_reglement_id = db.Column(db.Integer, nullable=True)

    # Relations
    utilisateurs = db.relationship("Utilisateur", back_populates="client", lazy="dynamic")
    adresses = db.relationship("Adresse", back_populates="client", lazy="dynamic")
    commandes = db.relationship("Commande", back_populates="client", lazy="dynamic")
    factures = db.relationship("Facture", back_populates="client", lazy="dynamic")
    reglements = db.relationship("Reglement", back_populates="client", lazy="dynamic")
    documents = db.relationship("Document", back_populates="client", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "nom": self.nom,
            "email": self.email,
            "telephone": self.telephone,
            "portable": self.portable,
            "numero_tva": self.numero_tva,
            "siret": self.siret,
            "site_web": self.site_web,
            "est_bloquer": self.est_bloquer,
            "est_pospect": self.est_pospect,
        }


# ============================================================
# 2. UTILISATEUR
# ============================================================
class Utilisateur(db.Model):
    __tablename__ = "utilisateur"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    roles = db.Column(db.String(255), nullable=True)  # ex: "client,admin" ou JSON sérialisé
    nom = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255), nullable=True)
    date_token = db.Column(db.DateTime, nullable=True)
    code_verification = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(30), nullable=True, default="actif")
    est_bloque = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    # Ajouté pour le portail
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=True, index=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Utilisé pour invalider automatiquement un lien de reset après usage :
    # le token de reset embarque cet horodatage ; s'il ne correspond plus à
    # la valeur en base (le mot de passe a été changé depuis), le lien est
    # considéré invalide même s'il n'a pas encore expiré (1h).
    password_changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)

    # Relations
    client = db.relationship("Client", back_populates="utilisateurs")
    ticketscrees = db.relationship("Ticket", back_populates="utilisateur", lazy="dynamic")
    notifications = db.relationship("NotificationErp", back_populates="utilisateur", lazy="dynamic")

    # --- Mot de passe ---
    def set_password(self, raw_password: str) -> None:
        self.password = bcrypt.generate_password_hash(raw_password).decode("utf-8")
        self.password_changed_at = datetime.utcnow()

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self.password, raw_password)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "nom": self.nom,
            "roles": self.roles,
            "status": self.status,
            "est_bloque": self.est_bloque,
            "client_id": self.client_id,
            "client": self.client.to_dict() if self.client else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ============================================================
# 3. ADRESSE
# ============================================================
class Adresse(db.Model):
    __tablename__ = "adresse"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False, index=True)
    adresse = db.Column(db.String(255), nullable=False)
    complement = db.Column(db.String(255), nullable=True)
    ville_id = db.Column(db.Integer, nullable=True)  # table `ville` non détaillée
    email = db.Column(db.String(255), nullable=True)
    societe = db.Column(db.String(255), nullable=True)
    est_default = db.Column(db.Boolean, default=False, nullable=False)
    est_livraison = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    client = db.relationship("Client", back_populates="adresses")


# ============================================================
# 4. ARTICLE
# ============================================================
class Article(db.Model):
    __tablename__ = "article"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom = db.Column(db.String(255), nullable=False)
    reference = db.Column(db.String(100), unique=True, nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)
    prix_vente_ht = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    prix_vente_ttc = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    est_affiche_ttc = db.Column(db.Boolean, default=True, nullable=False)
    est_service = db.Column(db.Boolean, default=False, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    est_bloque = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    tva_id = db.Column(db.Integer, db.ForeignKey("tva.id"), nullable=True)
    famille_article_id = db.Column(db.Integer, db.ForeignKey("famille_article.id"), nullable=True)
    sous_famille_article_id = db.Column(
        db.Integer, db.ForeignKey("sous_famille_article.id"), nullable=True
    )
    unite_id = db.Column(db.Integer, nullable=True)  # table `unite` non détaillée

    # Ajouté pour le portail
    stock_disponible = db.Column(db.Numeric(12, 3), nullable=False, default=0)

    tva = db.relationship("Tva", back_populates="articles")
    famille_article = db.relationship("FamilleArticle", back_populates="articles")
    sous_famille_article = db.relationship("SousFamilleArticle", back_populates="articles")


# ============================================================
# 5. FAMILLE_ARTICLE
# ============================================================
class FamilleArticle(db.Model):
    __tablename__ = "famille_article"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    libelle = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=True)
    est_service = db.Column(db.Boolean, default=False, nullable=False)
    est_default = db.Column(db.Boolean, default=False, nullable=False)
    est_desactive = db.Column(db.Boolean, default=False, nullable=False)

    articles = db.relationship("Article", back_populates="famille_article", lazy="dynamic")
    sous_familles = db.relationship(
        "SousFamilleArticle", back_populates="famille_article", lazy="dynamic"
    )


# ============================================================
# 6. SOUS_FAMILLE_ARTICLE
# ============================================================
class SousFamilleArticle(db.Model):
    __tablename__ = "sous_famille_article"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    famille_article_id = db.Column(
        db.Integer, db.ForeignKey("famille_article.id"), nullable=False
    )
    libelle = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), nullable=True)
    est_default = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    famille_article = db.relationship("FamilleArticle", back_populates="sous_familles")
    articles = db.relationship("Article", back_populates="sous_famille_article", lazy="dynamic")


# ============================================================
# 7. TVA
# ============================================================
class Tva(db.Model):
    __tablename__ = "tva"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(20), nullable=True)
    libelle = db.Column(db.String(100), nullable=False)
    valeur = db.Column(db.Numeric(5, 2), nullable=False, default=0)  # ex: 19.00 (%)
    est_default = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    articles = db.relationship("Article", back_populates="tva", lazy="dynamic")


# ============================================================
# 8. COMMANDE
# ============================================================
class Commande(db.Model):
    __tablename__ = "commande"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_commande = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_piece = db.Column(db.DateTime, nullable=True)
    date_echeance = db.Column(db.DateTime, nullable=True)
    total_ht = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    total_tva = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    total_ttc = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    est_valider = db.Column(db.Boolean, default=False, nullable=False)
    est_solder = db.Column(db.Boolean, default=False, nullable=False)
    montant_regle = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    solde_du = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False, index=True)
    status_id = db.Column(db.Integer, nullable=True)  # table `status` non détaillée
    cree_par_id = db.Column(db.Integer, db.ForeignKey("utilisateur.id"), nullable=True)

    client = db.relationship("Client", back_populates="commandes")
    lignes = db.relationship("ArticleCommande", back_populates="commande", lazy="dynamic")
    historique_statuts = db.relationship(
        "HistoriqueStatutCommande", back_populates="commande", lazy="dynamic"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero": self.numero,
            "date_commande": self.date_commande.isoformat() if self.date_commande else None,
            "total_ttc": float(self.total_ttc) if self.total_ttc is not None else None,
            "est_valider": self.est_valider,
            "est_solder": self.est_solder,
            "solde_du": float(self.solde_du) if self.solde_du is not None else None,
        }


# ============================================================
# 9. ARTICLE_COMMANDE
# ============================================================
class ArticleCommande(db.Model):
    __tablename__ = "article_commande"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    piece_id = db.Column(db.Integer, db.ForeignKey("commande.id"), nullable=False, index=True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=True)
    nom_article = db.Column(db.String(255), nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    quantite = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    prix_ht = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    prix_ttc = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    total_prix_ht = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    total_prix_ttc = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    taux_tva = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    valeur_tva = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    total_valeur_tva = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    taux_remise = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    valeur_remise = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    ordre = db.Column(db.Integer, nullable=False, default=0)
    est_commentaire = db.Column(db.Boolean, default=False, nullable=False)
    est_sous_total = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    commande = db.relationship("Commande", back_populates="lignes")


# ============================================================
# 10. FACTURE (même structure que commande + date_facture)
# ============================================================
class Facture(db.Model):
    __tablename__ = "facture"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_facture = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_piece = db.Column(db.DateTime, nullable=True)
    date_echeance = db.Column(db.DateTime, nullable=True)
    total_ht = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    total_tva = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    total_ttc = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    est_valider = db.Column(db.Boolean, default=False, nullable=False)
    est_solder = db.Column(db.Boolean, default=False, nullable=False)
    montant_regle = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    solde_du = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False, index=True)
    status_id = db.Column(db.Integer, nullable=True)
    cree_par_id = db.Column(db.Integer, db.ForeignKey("utilisateur.id"), nullable=True)

    client = db.relationship("Client", back_populates="factures")
    lignes = db.relationship("ArticleFacture", back_populates="facture", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero": self.numero,
            "date_facture": self.date_facture.isoformat() if self.date_facture else None,
            "date_echeance": self.date_echeance.isoformat() if self.date_echeance else None,
            "total_ttc": float(self.total_ttc) if self.total_ttc is not None else None,
            "est_solder": self.est_solder,
            "solde_du": float(self.solde_du) if self.solde_du is not None else None,
        }


# ============================================================
# 11. ARTICLE_FACTURE (même structure que article_commande)
# ============================================================
class ArticleFacture(db.Model):
    __tablename__ = "article_facture"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    piece_id = db.Column(db.Integer, db.ForeignKey("facture.id"), nullable=False, index=True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=True)
    nom_article = db.Column(db.String(255), nullable=True)
    reference = db.Column(db.String(100), nullable=True)
    quantite = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    prix_ht = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    prix_ttc = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    total_prix_ht = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    total_prix_ttc = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    taux_tva = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    valeur_tva = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    total_valeur_tva = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    taux_remise = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    valeur_remise = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    ordre = db.Column(db.Integer, nullable=False, default=0)
    est_commentaire = db.Column(db.Boolean, default=False, nullable=False)
    est_sous_total = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    facture = db.relationship("Facture", back_populates="lignes")


# ============================================================
# 12. BON_LIVRAISON
# ============================================================
class BonLivraison(db.Model):
    __tablename__ = "bon_livraison"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_livraison = db.Column(db.DateTime, nullable=True)
    date_piece = db.Column(db.DateTime, nullable=True)
    date_echeance = db.Column(db.DateTime, nullable=True)
    total_ht = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    total_tva = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    total_ttc = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    est_valider = db.Column(db.Boolean, default=False, nullable=False)
    est_imprimer = db.Column(db.Boolean, default=False, nullable=False)
    est_envoyer = db.Column(db.Boolean, default=False, nullable=False)
    est_desactive = db.Column(db.Boolean, default=False, nullable=False)

    tier_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=True, index=True)
    status_id = db.Column(db.Integer, nullable=True)
    mode_livraison_id = db.Column(db.Integer, nullable=True)  # table non détaillée

    adresse_livraison = db.Column(db.String(255), nullable=True)
    code_postal_livraison = db.Column(db.String(20), nullable=True)
    societe_livraison = db.Column(db.String(255), nullable=True)

    # Ajout portail
    transporteur = db.Column(db.String(100), nullable=True)
    numero_suivi = db.Column(db.String(100), nullable=True)

    lignes = db.relationship("ArticleBonLivraison", back_populates="bon_livraison", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero": self.numero,
            "date_livraison": self.date_livraison.isoformat() if self.date_livraison else None,
            "transporteur": self.transporteur,
            "numero_suivi": self.numero_suivi,
        }


# ============================================================
# 13. ARTICLE_BON_LIVRAISON
# ============================================================
class ArticleBonLivraison(db.Model):
    __tablename__ = "article_bon_livraison"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    piece_id = db.Column(
        db.Integer, db.ForeignKey("bon_livraison.id"), nullable=False, index=True
    )
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=True)
    nom_article = db.Column(db.String(255), nullable=True)
    code_article = db.Column(db.String(100), nullable=True)
    quantite = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    quantite_transferer = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    prix_ht = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    prix_ttc = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    total_prix_ht = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    total_prix_ttc = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    taux_tva = db.Column(db.Numeric(5, 2), nullable=False, default=0)
    valeur_tva = db.Column(db.Numeric(12, 3), nullable=False, default=0)
    est_sous_total = db.Column(db.Boolean, default=False, nullable=False)
    est_desactive = db.Column(db.Boolean, default=False, nullable=False)

    bon_livraison = db.relationship("BonLivraison", back_populates="lignes")


# ============================================================
# 14. REGLEMENT
# ============================================================
class Reglement(db.Model):
    __tablename__ = "reglement"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(50), unique=True, nullable=False, index=True)
    date_paiement = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    reference = db.Column(db.String(100), nullable=True)
    montant_regle = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    est_encaisser = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False, index=True)
    type_paiement_id = db.Column(db.Integer, nullable=True)  # table non détaillée
    mode_rgelement_id = db.Column(db.Integer, nullable=True)  # nom conservé tel que fourni

    client = db.relationship("Client", back_populates="reglements")
    details = db.relationship("DetailReglement", back_populates="reglement", lazy="dynamic")


# ============================================================
# 15. DETAIL_REGLEMENT
# ============================================================
class DetailReglement(db.Model):
    __tablename__ = "detail_reglement"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reglement_id = db.Column(
        db.Integer, db.ForeignKey("reglement.id"), nullable=False, index=True
    )
    piece_id = db.Column(db.Integer, nullable=False)  # référence commande OU facture
    type_piece = db.Column(db.String(20), nullable=False)  # "commande" | "facture"
    montant = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    date_echeance = db.Column(db.DateTime, nullable=True)
    numero_piece = db.Column(db.String(50), nullable=True)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    reglement = db.relationship("Reglement", back_populates="details")


# ============================================================
# 16. DOCUMENT
# ============================================================
class Document(db.Model):
    __tablename__ = "document"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False, index=True)
    lien = db.Column(db.String(500), nullable=False)
    nom = db.Column(db.String(255), nullable=False)
    est_attache_email = db.Column(db.Boolean, default=False, nullable=False)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    client = db.relationship("Client", back_populates="documents")


# ============================================================
# TABLES FINANCE — ajoutées pour les cartes du tableau de bord
# (dépenses, comptes bancaires, factures d'achats). Aucune donnée
# de départ : chaque carte affiche 0 tant que rien n'est saisi,
# exactement comme un ERP neuf sans écritures.
# ============================================================


class Depense(db.Model):
    __tablename__ = "depense"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    libelle = db.Column(db.String(255), nullable=False)
    montant = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    date_depense = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    categorie = db.Column(db.String(100), nullable=True)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)


class CompteBancaire(db.Model):
    __tablename__ = "compte_bancaire"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nom_banque = db.Column(db.String(255), nullable=False)
    numero_compte = db.Column(db.String(100), nullable=True)
    solde = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)


class FactureAchat(db.Model):
    __tablename__ = "facture_achat"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    date_facture = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    montant_ht = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    montant_ttc = db.Column(db.Numeric(14, 3), nullable=False, default=0)
    fournisseur_id = db.Column(db.Integer, nullable=True)  # table `fournisseur` pas encore définie
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)


# ============================================================
# TABLES SPÉCIFIQUES AU PORTAIL
# ============================================================


class Panier(db.Model):
    __tablename__ = "panier"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False, index=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("utilisateur.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    lignes = db.relationship("ArticlePanier", back_populates="panier", lazy="dynamic")


class ArticlePanier(db.Model):
    __tablename__ = "article_panier"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    panier_id = db.Column(db.Integer, db.ForeignKey("panier.id"), nullable=False, index=True)
    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=False)
    quantite = db.Column(db.Numeric(12, 3), nullable=False, default=1)
    prix_unitaire_ht = db.Column(db.Numeric(12, 3), nullable=False, default=0)

    panier = db.relationship("Panier", back_populates="lignes")


class HistoriqueStatutCommande(db.Model):
    __tablename__ = "historique_statut_commande"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    commande_id = db.Column(
        db.Integer, db.ForeignKey("commande.id"), nullable=False, index=True
    )
    ancien_status_id = db.Column(db.Integer, nullable=True)
    nouveau_status_id = db.Column(db.Integer, nullable=True)
    date_changement = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    commentaire = db.Column(db.String(500), nullable=True)

    commande = db.relationship("Commande", back_populates="historique_statuts")


class Ticket(db.Model):
    __tablename__ = "ticket"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"), nullable=False, index=True)
    utilisateur_id = db.Column(
        db.Integer, db.ForeignKey("utilisateur.id"), nullable=False, index=True
    )
    sujet = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    categorie = db.Column(db.String(100), nullable=True)
    priorite = db.Column(db.String(20), nullable=False, default="normale")
    status = db.Column(db.String(30), nullable=False, default="ouvert")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    est_supprime = db.Column(db.Boolean, default=False, nullable=False)

    utilisateur = db.relationship("Utilisateur", back_populates="ticketscrees")
    messages = db.relationship("MessageTicket", back_populates="ticket", lazy="dynamic")
    pieces_jointes = db.relationship("PieceJointe", back_populates="ticket", lazy="dynamic")


class MessageTicket(db.Model):
    __tablename__ = "message_ticket"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=False, index=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("utilisateur.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    est_interne = db.Column(db.Boolean, default=False, nullable=False)  # note interne (non visible client)

    ticket = db.relationship("Ticket", back_populates="messages")


class NotificationErp(db.Model):
    """
    Table `notification` du schéma ERP/portail.
    Renommée en NotificationErp côté Python uniquement (le nom de la table
    SQL reste `notification`) pour éviter un conflit avec la classe
    `Notification` déjà existante dans app/models.py (notifications locales
    du portail, table `notifications`). À terme, il faudra choisir laquelle
    des deux devient la source de vérité unique.
    """

    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    utilisateur_id = db.Column(
        db.Integer, db.ForeignKey("utilisateur.id"), nullable=False, index=True
    )
    type = db.Column(db.String(50), nullable=False)
    titre = db.Column(db.String(255), nullable=False)
    message = db.Column(db.String(500), nullable=True)
    lien = db.Column(db.String(255), nullable=True)
    est_lu = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    utilisateur = db.relationship("Utilisateur", back_populates="notifications")


class PieceJointe(db.Model):
    __tablename__ = "piece_jointe"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Rattachement polymorphe : peut être liée à un ticket, une demande d'avoir, etc.
    ticket_id = db.Column(db.Integer, db.ForeignKey("ticket.id"), nullable=True, index=True)
    entite_type = db.Column(db.String(50), nullable=True)  # ex: "ticket", "demande_avoir"
    entite_id = db.Column(db.Integer, nullable=True)

    nom_fichier = db.Column(db.String(255), nullable=False)
    lien = db.Column(db.String(500), nullable=False)
    type_mime = db.Column(db.String(100), nullable=True)
    taille_octets = db.Column(db.Integer, nullable=True)
    uploaded_par_id = db.Column(db.Integer, db.ForeignKey("utilisateur.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    ticket = db.relationship("Ticket", back_populates="pieces_jointes")


class JournalAudit(db.Model):
    __tablename__ = "journal_audit"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    utilisateur_id = db.Column(
        db.Integer, db.ForeignKey("utilisateur.id"), nullable=True, index=True
    )
    action = db.Column(db.String(100), nullable=False)  # ex: "connexion", "telechargement", "paiement"
    entite = db.Column(db.String(100), nullable=True)  # ex: "facture", "commande"
    entite_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON sérialisé si besoin
    adresse_ip = db.Column(db.String(45), nullable=True)  # IPv4 ou IPv6
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
