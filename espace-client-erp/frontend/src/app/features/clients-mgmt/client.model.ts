export interface ClientRecord {
  id: number;
  code: string | null;
  nom: string;
  email: string | null;
  telephone: string | null;
  portable: string | null;
  numero_tva: string | null;
  siret: string | null;
  site_web: string | null;
  est_bloquer: boolean;
  est_pospect: boolean;
}
