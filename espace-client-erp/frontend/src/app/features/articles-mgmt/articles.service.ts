import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { ArticleOptions, ArticleRecord } from './article.model';

@Injectable({ providedIn: 'root' })
export class ArticlesService {
  constructor(private http: HttpClient) {}

  list(): Observable<{ articles: ArticleRecord[] }> {
    return this.http.get<{ articles: ArticleRecord[] }>(`${environment.apiUrl}/articles`);
  }

  options(): Observable<ArticleOptions> {
    return this.http.get<ArticleOptions>(`${environment.apiUrl}/articles/options/familles`);
  }

  create(payload: Partial<ArticleRecord>): Observable<{ article: ArticleRecord }> {
    return this.http.post<{ article: ArticleRecord }>(`${environment.apiUrl}/articles`, payload);
  }

  update(id: number, payload: Partial<ArticleRecord>): Observable<{ article: ArticleRecord }> {
    return this.http.put<{ article: ArticleRecord }>(`${environment.apiUrl}/articles/${id}`, payload);
  }

  delete(id: number): Observable<{ message: string }> {
    return this.http.delete<{ message: string }>(`${environment.apiUrl}/articles/${id}`);
  }
}
