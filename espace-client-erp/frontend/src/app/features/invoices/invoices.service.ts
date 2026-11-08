import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { InvoiceDetail, InvoiceListItem } from './invoice.model';

@Injectable({ providedIn: 'root' })
export class InvoicesService {
  constructor(private http: HttpClient) {}

  list(): Observable<{ invoices: InvoiceListItem[]; erp_errors?: string[] }> {
    return this.http.get<{ invoices: InvoiceListItem[]; erp_errors?: string[] }>(
      `${environment.apiUrl}/invoices`,
    );
  }

  get(id: number): Observable<{ invoice: InvoiceDetail }> {
    return this.http.get<{ invoice: InvoiceDetail }>(`${environment.apiUrl}/invoices/${id}`);
  }

  downloadPdf(id: number): Observable<Blob> {
    return this.http.get(`${environment.apiUrl}/invoices/${id}/pdf`, { responseType: 'blob' });
  }
}
