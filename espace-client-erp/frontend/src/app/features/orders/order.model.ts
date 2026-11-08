export interface OrderLine {
  nom_article: string;
  reference: string | null;
  quantite: number;
  prix_ht: number;
  total_prix_ttc: number;
}

export interface StatusHistoryEntry {
  ancien_status_id: number | null;
  nouveau_status_id: number | null;
  date_changement: string | null;
  commentaire: string | null;
}

export interface OrderListItem {
  id: number;
  numero: string;
  date_commande: string | null;
  total_ttc: number;
  est_valider: boolean;
  est_solder: boolean;
  solde_du: number;
}

export interface OrderDetail extends OrderListItem {
  lignes: OrderLine[];
  historique_statuts: StatusHistoryEntry[];
}
