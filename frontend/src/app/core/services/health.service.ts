import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, first, interval, map, of, switchMap, timeout } from 'rxjs';

import { environment } from '../../../environments/environment';

export type HealthPollResult = 'healthy' | 'timeout';

const POLL_INTERVAL_MS = 2500;
const POLL_TIMEOUT_MS = 90000;

@Injectable({ providedIn: 'root' })
export class HealthService {
  private readonly http = inject(HttpClient);
  private readonly healthUrl = `${environment.apiBaseUrl.replace(/\/api\/v1\/?$/, '')}/health`;

  checkOnce(): Observable<boolean> {
    return this.http.get(this.healthUrl).pipe(
      map(() => true),
      catchError(() => of(false)),
    );
  }

  pollUntilHealthy(): Observable<HealthPollResult> {
    return interval(POLL_INTERVAL_MS).pipe(
      switchMap(() => this.checkOnce()),
      first((ok) => ok),
      map(() => 'healthy' as const),
      timeout(POLL_TIMEOUT_MS),
      catchError(() => of('timeout' as const)),
    );
  }
}
