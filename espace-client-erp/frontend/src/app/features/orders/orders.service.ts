import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { OrderDetail, OrderListItem } from './order.model';

@Injectable({ providedIn: 'root' })
export class OrdersService {
  constructor(private http: HttpClient) {}

  list(): Observable<{ orders: OrderListItem[]; erp_errors?: string[] }> {
    return this.http.get<{ orders: OrderListItem[]; erp_errors?: string[] }>(
      `${environment.apiUrl}/orders`,
    );
  }

  get(id: number): Observable<{ order: OrderDetail }> {
    return this.http.get<{ order: OrderDetail }>(`${environment.apiUrl}/orders/${id}`);
  }

  downloadPdf(id: number): Observable<Blob> {
    return this.http.get(`${environment.apiUrl}/orders/${id}/pdf`, { responseType: 'blob' });
  }
}
