/**
 * Dictionnaire de traductions FR/EN pour toute l'application.
 * Organisé par section pour rester lisible malgré le volume.
 */
export type Lang = 'fr' | 'en';

export const TRANSLATIONS: Record<string, Record<Lang, string>> = {
  // --- Marque / commun ---
  'app.brand': { fr: 'Espace Client', en: 'Customer Portal' },
  'common.loading': { fr: 'Chargement…', en: 'Loading…' },
  'common.retry': { fr: 'Réessayer', en: 'Retry' },
  'common.save': { fr: 'Enregistrer', en: 'Save' },
  'common.cancel': { fr: 'Annuler', en: 'Cancel' },
  'common.delete': { fr: 'Supprimer', en: 'Delete' },
  'common.edit': { fr: 'Modifier', en: 'Edit' },
  'common.close': { fr: 'Fermer', en: 'Close' },
  'common.back': { fr: 'Retour', en: 'Back' },
  'common.currency': { fr: 'TND', en: 'TND' },
  'common.none': { fr: 'Aucun', en: 'None' },

  // --- Nav bar (sidebar + topbar) ---
  'nav.dashboard': { fr: 'Tableau de bord', en: 'Dashboard' },
  'nav.orders': { fr: 'Commandes', en: 'Orders' },
  'nav.invoices': { fr: 'Factures', en: 'Invoices' },
  'nav.clients': { fr: 'Clients', en: 'Clients' },
  'nav.articles': { fr: 'Articles', en: 'Articles' },
  'nav.sales': { fr: 'Ventes', en: 'Sales' },
  'nav.funds': { fr: 'Fonds', en: 'Funds' },
  'nav.treasury': { fr: 'Trésorerie', en: 'Treasury' },
  'nav.accounting': { fr: 'Comptabilité', en: 'Accounting' },
  'nav.activities': { fr: 'Activités', en: 'Activities' },
  'nav.notifications': { fr: 'Notifications', en: 'Notifications' },
  'nav.logout': { fr: 'Déconnexion', en: 'Log out' },
  'nav.language': { fr: 'Langue', en: 'Language' },

  // --- Login ---
  'login.title': { fr: 'Connexion à votre compte', en: 'Sign in to your account' },
  'login.subtitle': {
    fr: 'Accédez à vos commandes, factures et documents.',
    en: 'Access your orders, invoices and documents.',
  },
  'login.email': { fr: 'Email', en: 'Email' },
  'login.password': { fr: 'Mot de passe', en: 'Password' },
  'login.forgot': { fr: 'Mot de passe oublié ?', en: 'Forgot password?' },
  'login.submit': { fr: 'Se connecter', en: 'Sign in' },
  'login.submitting': { fr: 'Connexion en cours…', en: 'Signing in…' },
  'login.noAccount': { fr: "Pas encore de compte ?", en: "Don't have an account?" },
  'login.createAccount': { fr: 'Créer un compte', en: 'Create an account' },
  'login.emailInvalid': { fr: 'Veuillez saisir un email valide.', en: 'Please enter a valid email.' },
  'login.passwordRequired': { fr: 'Le mot de passe est requis.', en: 'Password is required.' },
  'login.genericError': {
    fr: 'Une erreur est survenue. Veuillez réessayer.',
    en: 'Something went wrong. Please try again.',
  },

  // --- Register ---
  'register.title': { fr: 'Créer votre compte', en: 'Create your account' },
  'register.subtitle': {
    fr: 'Accédez à vos commandes, factures et documents en ligne.',
    en: 'Access your orders, invoices and documents online.',
  },
  'register.firstName': { fr: 'Prénom', en: 'First name' },
  'register.lastName': { fr: 'Nom', en: 'Last name' },
  'register.email': { fr: 'Email professionnel', en: 'Business email' },
  'register.phone': { fr: 'Téléphone (optionnel)', en: 'Phone (optional)' },
  'register.password': { fr: 'Mot de passe', en: 'Password' },
  'register.passwordHint': {
    fr: '8 caractères min., une majuscule, une minuscule, un chiffre, un caractère spécial.',
    en: 'Min. 8 characters, one uppercase, one lowercase, one digit, one special character.',
  },
  'register.passwordInvalid': {
    fr: 'Le mot de passe ne respecte pas les critères requis.',
    en: 'The password does not meet the required criteria.',
  },
  'register.confirmPassword': { fr: 'Confirmer le mot de passe', en: 'Confirm password' },
  'register.passwordMismatch': {
    fr: 'Les mots de passe ne correspondent pas.',
    en: 'Passwords do not match.',
  },
  'register.submit': { fr: 'Créer mon compte', en: 'Create my account' },
  'register.submitting': { fr: 'Création en cours…', en: 'Creating…' },
  'register.haveAccount': { fr: 'Déjà un compte ?', en: 'Already have an account?' },
  'register.signIn': { fr: 'Se connecter', en: 'Sign in' },
  'register.genericError': {
    fr: 'Une erreur est survenue. Veuillez réessayer.',
    en: 'Something went wrong. Please try again.',
  },

  // --- Forgot password ---
  'forgot.title': { fr: 'Mot de passe oublié', en: 'Forgot password' },
  'forgot.subtitle': {
    fr: 'Indiquez votre email, nous vous enverrons un lien de réinitialisation.',
    en: "Enter your email and we'll send you a reset link.",
  },
  'forgot.email': { fr: 'Email', en: 'Email' },
  'forgot.submit': { fr: 'Envoyer le lien', en: 'Send link' },
  'forgot.submitting': { fr: 'Envoi en cours…', en: 'Sending…' },
  'forgot.backToLogin': { fr: 'Retour à la connexion', en: 'Back to sign in' },
  'forgot.success': {
    fr: "Un email de réinitialisation vient d'être envoyé.",
    en: 'A password reset email has just been sent.',
  },

  // --- Dashboard ---
  'dashboard.greeting': { fr: 'Bonjour', en: 'Hello' },
  'dashboard.loading': { fr: 'Chargement de votre tableau de bord…', en: 'Loading your dashboard…' },
  'dashboard.errorLoad': {
    fr: 'Impossible de charger le tableau de bord pour le moment. Veuillez réessayer.',
    en: 'Unable to load the dashboard right now. Please try again.',
  },
  'dashboard.notLinked': {
    fr: "Votre compte n'est pas encore relié à votre fiche client ERP. Certaines informations ne sont pas disponibles pour le moment.",
    en: 'Your account is not yet linked to an ERP customer record. Some information may be unavailable.',
  },
  'dashboard.balance': { fr: 'Solde du compte', en: 'Account balance' },
  'dashboard.notAvailable': { fr: 'Non disponible', en: 'Not available' },
  'dashboard.salesInvoices': { fr: 'Factures Ventes', en: 'Sales Invoices' },
  'dashboard.purchaseInvoices': { fr: "Factures d'achats", en: 'Purchase Invoices' },
  'dashboard.expenses': { fr: 'Dépenses', en: 'Expenses' },
  'dashboard.grossMargin': { fr: 'Marge brute', en: 'Gross margin' },
  'dashboard.netMargin': { fr: 'Marge nette', en: 'Net margin' },
  'dashboard.bankAccounts': { fr: 'Comptes bancaires', en: 'Bank accounts' },
  'dashboard.noBankAccount': { fr: 'Aucun compte bancaire enregistré', en: 'No bank account on record' },
  'dashboard.treasuryBalance': { fr: 'Solde de trésorerie actuelle', en: 'Current treasury balance' },

  // --- KPIs (nouveau dashboard ERP) ---
  'kpi.revenue': { fr: "Chiffre d'affaires (mois)", en: 'Revenue (month)' },
  'kpi.orders': { fr: 'Commandes (mois)', en: 'Orders (month)' },
  'kpi.clients': { fr: 'Clients', en: 'Clients' },
  'kpi.newClients': { fr: 'Nouveaux clients (mois)', en: 'New clients (month)' },
  'kpi.paidInvoices': { fr: 'Factures payées', en: 'Paid invoices' },
  'kpi.unpaidInvoices': { fr: 'Factures impayées', en: 'Unpaid invoices' },
  'kpi.expenses': { fr: 'Dépenses (mois)', en: 'Expenses (month)' },
  'kpi.treasury': { fr: 'Trésorerie', en: 'Treasury' },
  'kpi.grossMargin': { fr: 'Marge brute (mois)', en: 'Gross margin (month)' },
  'kpi.netMargin': { fr: 'Marge nette (mois)', en: 'Net margin (month)' },
  'kpi.articles': { fr: 'Articles', en: 'Items' },

  'charts.revenueVsExpenses': { fr: 'Ventes vs Dépenses (6 derniers mois)', en: 'Sales vs Expenses (last 6 months)' },
  'charts.profitEvolution': { fr: 'Évolution du bénéfice', en: 'Profit evolution' },

  'quickActions.title': { fr: 'Actions rapides', en: 'Quick actions' },

  'topClients.title': { fr: 'Meilleurs clients', en: 'Top clients' },
  'topClients.empty': { fr: 'Aucune donnée disponible.', en: 'No data available.' },
  'topArticles.title': { fr: 'Articles les plus vendus', en: 'Best-selling items' },
  'topArticles.empty': { fr: 'Aucune donnée disponible.', en: 'No data available.' },
  'topArticles.quantitySold': { fr: 'vendu(s)', en: 'sold' },

  'recentInvoices.title': { fr: 'Dernières factures', en: 'Latest invoices' },
  'recentOrders.title': { fr: 'Dernières commandes', en: 'Latest orders' },

  'darkMode.toggle': { fr: 'Mode sombre', en: 'Dark mode' },

  // --- Orders ---
  'orders.title': { fr: 'Mes commandes', en: 'My orders' },
  'orders.empty': { fr: "Vous n'avez aucune commande pour le moment.", en: 'You have no orders yet.' },
  'orders.errorLoad': { fr: 'Impossible de charger vos commandes pour le moment.', en: 'Unable to load your orders right now.' },
  'orders.number': { fr: 'N° commande', en: 'Order No.' },
  'orders.date': { fr: 'Date', en: 'Date' },
  'orders.status': { fr: 'Statut', en: 'Status' },
  'orders.totalTtc': { fr: 'Total TTC', en: 'Total incl. tax' },
  'orders.balanceDue': { fr: 'Solde dû', en: 'Balance due' },
  'orders.validated': { fr: 'Validée', en: 'Validated' },
  'orders.pending': { fr: 'En attente', en: 'Pending' },
  'orders.pdf': { fr: 'PDF', en: 'PDF' },
  'orders.backToList': { fr: '← Retour aux commandes', en: '← Back to orders' },
  'orders.errorDetail': { fr: 'Impossible de charger cette commande.', en: 'Unable to load this order.' },
  'orders.downloadPdf': { fr: 'Télécharger le PDF', en: 'Download PDF' },
  'orders.generating': { fr: 'Génération...', en: 'Generating...' },
  'orders.articles': { fr: 'Articles', en: 'Items' },
  'orders.article': { fr: 'Article', en: 'Item' },
  'orders.reference': { fr: 'Référence', en: 'Reference' },
  'orders.quantity': { fr: 'Quantité', en: 'Quantity' },
  'orders.priceHt': { fr: 'Prix HT', en: 'Unit price (excl. tax)' },
  'orders.noLines': { fr: "Aucune ligne d'article.", en: 'No line items.' },
  'orders.statusHistory': { fr: 'Historique du statut', en: 'Status history' },
  'orders.oldStatus': { fr: 'Ancien statut', en: 'Previous status' },
  'orders.newStatus': { fr: 'Nouveau statut', en: 'New status' },
  'orders.comment': { fr: 'Commentaire', en: 'Comment' },
  'orders.noHistory': {
    fr: 'Aucun changement de statut enregistré pour cette commande.',
    en: 'No status change recorded for this order.',
  },

  // --- Invoices ---
  'invoices.title': { fr: 'Mes factures', en: 'My invoices' },
  'invoices.empty': { fr: "Vous n'avez aucune facture pour le moment.", en: 'You have no invoices yet.' },
  'invoices.errorLoad': { fr: 'Impossible de charger vos factures pour le moment.', en: 'Unable to load your invoices right now.' },
  'invoices.number': { fr: 'N° facture', en: 'Invoice No.' },
  'invoices.date': { fr: 'Date', en: 'Date' },
  'invoices.dueDate': { fr: 'Échéance', en: 'Due date' },
  'invoices.status': { fr: 'Statut', en: 'Status' },
  'invoices.totalTtc': { fr: 'Total TTC', en: 'Total incl. tax' },
  'invoices.settled': { fr: 'Soldée', en: 'Settled' },
  'invoices.pending': { fr: 'En attente', en: 'Pending' },
  'invoices.backToList': { fr: '← Retour aux factures', en: '← Back to invoices' },
  'invoices.errorDetail': { fr: 'Impossible de charger cette facture.', en: 'Unable to load this invoice.' },
  'invoices.balanceDue': { fr: 'Solde dû', en: 'Balance due' },

  // --- Clients ---
  'clients.title': { fr: 'Clients', en: 'Clients' },
  'clients.new': { fr: '+ Nouveau client', en: '+ New client' },
  'clients.errorLoad': { fr: 'Impossible de charger la liste des clients.', en: 'Unable to load the client list.' },
  'clients.errorCreate': {
    fr: 'Impossible de créer ce client. Vérifiez les champs.',
    en: 'Unable to create this client. Please check the fields.',
  },
  'clients.empty': { fr: 'Aucun client enregistré.', en: 'No clients on record.' },
  'clients.name': { fr: 'Nom', en: 'Name' },
  'clients.email': { fr: 'Email', en: 'Email' },
  'clients.phone': { fr: 'Téléphone', en: 'Phone' },
  'clients.vat': { fr: 'N° TVA', en: 'VAT No.' },
  'clients.siret': { fr: 'SIRET', en: 'Registration No.' },
  'clients.status': { fr: 'Statut', en: 'Status' },
  'clients.blocked': { fr: 'Bloqué', en: 'Blocked' },
  'clients.active': { fr: 'Actif', en: 'Active' },
  'clients.creating': { fr: 'Création...', en: 'Creating...' },
  'clients.createBtn': { fr: 'Créer le client', en: 'Create client' },

  // --- Articles ---
  'articles.title': { fr: 'Gestion des articles', en: 'Product management' },
  'articles.new': { fr: '+ Nouvel article', en: '+ New item' },
  'articles.errorLoad': { fr: 'Impossible de charger la liste des articles.', en: 'Unable to load the item list.' },
  'articles.errorCreate': {
    fr: 'Impossible de créer cet article. Vérifiez les champs.',
    en: 'Unable to create this item. Please check the fields.',
  },
  'articles.empty': { fr: 'Aucun article enregistré.', en: 'No items on record.' },
  'articles.name': { fr: 'Article', en: 'Item' },
  'articles.reference': { fr: 'Référence', en: 'Reference' },
  'articles.family': { fr: 'Famille', en: 'Category' },
  'articles.priceHt': { fr: 'Prix HT', en: 'Price (excl. tax)' },
  'articles.priceTtc': { fr: 'Prix de vente TTC', en: 'Selling price (incl. tax)' },
  'articles.stock': { fr: 'Stock', en: 'Stock' },
  'articles.stockAvailable': { fr: 'Stock disponible', en: 'Available stock' },
  'articles.vat': { fr: 'TVA', en: 'VAT' },
  'articles.creating': { fr: 'Création...', en: 'Creating...' },
  'articles.createBtn': { fr: "Créer l'article", en: 'Create item' },
  'articles.deleteConfirm': { fr: 'Supprimer l\'article "{name}" ?', en: 'Delete item "{name}"?' },

  // --- Notifications ---
  'notifications.title': { fr: 'Notifications', en: 'Notifications' },
  'notifications.markAllRead': { fr: 'Tout marquer comme lu', en: 'Mark all as read' },
  'notifications.viewAll': { fr: 'Voir tout', en: 'View all' },
  'notifications.empty': { fr: 'Aucune notification pour le moment.', en: 'You have no notifications yet.' },
  'notifications.noNotifications': { fr: 'Aucune notification pour le moment.', en: 'You have no notifications yet.' },
  'notifications.errorLoad': {
    fr: 'Impossible de charger vos notifications pour le moment.',
    en: 'Unable to load your notifications right now.',
  },

  // --- Coming soon ---
  'comingSoon.text': {
    fr: 'Ce module est en cours de construction. Il sera bientôt disponible.',
    en: 'This module is under construction. It will be available soon.',
  },

  // --- Chatbot ---
  'chatbot.title': { fr: 'Assistant Espace Client', en: 'Customer Portal Assistant' },
  'chatbot.greeting': {
    fr: 'Bonjour 👋 Je peux vous renseigner sur votre solde, vos commandes, vos factures, vos documents ou vos notifications.',
    en: 'Hello 👋 I can help you with your balance, orders, invoices, documents or notifications.',
  },
  'chatbot.placeholder': {
    fr: 'Posez votre question (solde, commandes, factures...)',
    en: 'Ask a question (balance, orders, invoices...)',
  },
  'chatbot.send': { fr: 'Envoyer', en: 'Send' },
  'chatbot.error': {
    fr: 'Désolé, une erreur est survenue. Veuillez réessayer.',
    en: 'Sorry, something went wrong. Please try again.',
  },
};
