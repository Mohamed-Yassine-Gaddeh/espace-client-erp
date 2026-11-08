import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { NotificationItem } from './notification.model';

@Injectable({ providedIn: 'root' })
export class NotificationsService {
  constructor(private http: HttpClient) {}

  list(): Observable<{ notifications: NotificationItem[]; unread_count: number }> {
    return this.http.get<{ notifications: NotificationItem[]; unread_count: number }>(
      `${environment.apiUrl}/notifications`,
    );
  }

  markRead(id: number): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(
      `${environment.apiUrl}/notifications/${id}/read`,
      {},
    );
  }

  markAllRead(): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${environment.apiUrl}/notifications/read-all`, {});
  }
}
