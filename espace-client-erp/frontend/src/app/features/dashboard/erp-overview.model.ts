export interface KpiValue {
  valeur: number;
  variation: number | null;
}

export interface ErpKpis {
  chiffre_affaires: KpiValue;
  nb_commandes: KpiValue;
  nb_clients: KpiValue;
  nouveaux_clients: KpiValue;
  factures_payees: KpiValue;
  factures_impayees: KpiValue;
  depenses: KpiValue;
  tresorerie: KpiValue;
  marge_brute: KpiValue;
  marge_nette: KpiValue;
  nb_articles: KpiValue;
}

export interface ErpCharts {
  labels: string[];
  chiffre_affaires_mensuel: number[];
  depenses_mensuel: number[];
  benefice_mensuel: number[];
}

export interface TopClient {
  id: number;
  nom: string;
  total: number;
}

export interface TopArticle {
  nom: string;
  quantite: number;
  montant: number;
}

export interface RecentFactureRow {
  id: number;
  numero: string;
  date_facture: string | null;
  total_ttc: number;
  est_solder: boolean;
  solde_du: number;
}

export interface RecentCommandeRow {
  id: number;
  numero: string;
  date_commande: string | null;
  total_ttc: number;
  est_valider: boolean;
  solde_du: number;
}

export interface ErpOverview {
  kpis: ErpKpis;
  charts: ErpCharts;
  top_clients: TopClient[];
  top_articles: TopArticle[];
  dernieres_factures: RecentFactureRow[];
  dernieres_commandes: RecentCommandeRow[];
  currency: string;
}
