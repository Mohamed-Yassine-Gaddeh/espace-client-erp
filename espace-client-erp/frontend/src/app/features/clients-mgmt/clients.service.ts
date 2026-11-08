import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ClientRecord } from './client.model';

@Injectable({ providedIn: 'root' })
export class ClientsService {
  constructor(private http: HttpClient) {}

  list(): Observable<{ clients: ClientRecord[] }> {
    return this.http.get<{ clients: ClientRecord[] }>(`${environment.apiUrl}/clients`);
  }

  get(id: number): Observable<{ client: ClientRecord }> {
    return this.http.get<{ client: ClientRecord }>(`${environment.apiUrl}/clients/${id}`);
  }

  create(payload: Partial<ClientRecord>): Observable<{ client: ClientRecord }> {
    return this.http.post<{ client: ClientRecord }>(`${environment.apiUrl}/clients`, payload);
  }

  update(id: number, payload: Partial<ClientRecord>): Observable<{ client: ClientRecord }> {
    return this.http.put<{ client: ClientRecord }>(`${environment.apiUrl}/clients/${id}`, payload);
  }
}
