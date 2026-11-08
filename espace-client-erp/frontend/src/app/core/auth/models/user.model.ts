export interface ClientInfo {
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

export interface User {
  id: number;
  email: string;
  nom: string;
  roles: string | null;
  status: string | null;
  est_bloque: boolean;
  client_id: number | null;
  client: ClientInfo | null;
  created_at: string | null;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token: string;
}

export interface ApiErrorResponse {
  errors: Record<string, string>;
}

export interface RegisterPayload {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  password: string;
  password_confirmation: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}
