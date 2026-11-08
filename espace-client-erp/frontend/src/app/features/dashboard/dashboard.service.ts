import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { DashboardSummary } from './dashboard.model';
import { ErpOverview } from './erp-overview.model';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  constructor(private http: HttpClient) {}

  getSummary(): Observable<DashboardSummary> {
    return this.http.get<DashboardSummary>(`${environment.apiUrl}/dashboard/summary`);
  }

  getErpOverview(): Observable<ErpOverview> {
    return this.http.get<ErpOverview>(`${environment.apiUrl}/dashboard/erp-overview`);
  }

  markNotificationRead(notificationId: number): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${environment.apiUrl}/dashboard/notifications/${notificationId}/read`,
      {},
    );
  }
}
