export interface InvoiceLine {
  nom_article: string;
  reference: string | null;
  quantite: number;
  prix_ht: number;
  total_prix_ttc: number;
}

export interface InvoiceListItem {
  id: number;
  numero: string;
  date_facture: string | null;
  date_echeance: string | null;
  total_ttc: number;
  est_solder: boolean;
  solde_du: number;
}

export interface InvoiceDetail extends InvoiceListItem {
  lignes: InvoiceLine[];
}
