import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { RelatedSession, SessionDetailResponse, SessionListItem, SessionResponse } from '../models/session.model';

@Injectable({ providedIn: 'root' })
export class SessionService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = `${environment.apiBaseUrl}/sessions`;

  createFromText(text: string, roundsPlanned = 3): Observable<SessionResponse> {
    return this.http.post<SessionResponse>(this.baseUrl, { text, rounds_planned: roundsPlanned });
  }

  createFromFile(file: File, roundsPlanned = 3): Observable<SessionResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('rounds_planned', String(roundsPlanned));
    return this.http.post<SessionResponse>(`${this.baseUrl}/upload`, formData);
  }

  list(): Observable<SessionListItem[]> {
    return this.http.get<SessionListItem[]>(this.baseUrl);
  }

  get(sessionId: string): Observable<SessionDetailResponse> {
    return this.http.get<SessionDetailResponse>(`${this.baseUrl}/${sessionId}`);
  }

  related(sessionId: string): Observable<RelatedSession[]> {
    return this.http.get<RelatedSession[]>(`${this.baseUrl}/${sessionId}/related`);
  }
}
