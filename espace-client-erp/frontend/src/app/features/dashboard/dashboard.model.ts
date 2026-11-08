export interface Balance {
  balance: number;
  currency: string;
}

export interface OrderSummary {
  id: number;
  reference: string;
  date: string;
  status: string;
  total: number;
}

export interface InvoiceSummary {
  id: number;
  number: string;
  date: string;
  due_date: string;
  amount: number;
  payment_status: string;
}

export interface DocumentSummary {
  id: number;
  type: string;
  name: string;
  date: string;
  download_url: string;
}

export interface DashboardNotification {
  id: number;
  type: string;
  title: string;
  message: string | null;
  link: string | null;
  is_read: boolean;
  created_at: string;
}

export interface CompteBancaireSummary {
  id: number;
  nom_banque: string;
  solde: number;
}

export interface FinanceSummary {
  factures_ventes_total: number;
  factures_achats_total: number;
  depenses_total: number;
  marge_brute: number;
  marge_nette: number;
  comptes_bancaires: CompteBancaireSummary[];
  solde_tresorerie_actuelle: number;
  currency: string;
}

export interface DashboardSummary {
  customer_name: string;
  erp_linked: boolean;
  balance: Balance | null;
  recent_orders: OrderSummary[];
  recent_invoices: InvoiceSummary[];
  recent_documents: DocumentSummary[];
  order_status_summary: Record<string, number>;
  notifications: DashboardNotification[];
  unread_notifications_count: number;
  erp_errors: string[];
  finance: FinanceSummary;
}
