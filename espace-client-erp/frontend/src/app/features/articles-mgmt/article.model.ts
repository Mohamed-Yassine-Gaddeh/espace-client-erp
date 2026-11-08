export interface ArticleRecord {
  id: number;
  nom: string;
  reference: string | null;
  description: string | null;
  prix_vente_ht: number;
  prix_vente_ttc: number;
  est_service: boolean;
  est_bloque: boolean;
  stock_disponible: number;
  tva_id: number | null;
  famille_article_id: number | null;
  sous_famille_article_id: number | null;
  famille_libelle: string | null;
  tva_valeur: number | null;
}

export interface ArticleOptions {
  familles: { id: number; libelle: string }[];
  tvas: { id: number; libelle: string; valeur: number }[];
}
