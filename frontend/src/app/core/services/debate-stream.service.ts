import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { DebateEvent } from '../models/debate-event.model';

@Injectable({ providedIn: 'root' })
export class DebateStreamService {
  /**
   * Consumes the SSE stream via fetch + ReadableStream (not EventSource — we don't
   * need to POST/customize here, but this keeps parsing consistent and lets us
   * cancel mid-stream via the returned teardown).
   */
  stream(sessionId: string): Observable<DebateEvent> {
    return new Observable<DebateEvent>((subscriber) => {
      const controller = new AbortController();

      fetch(`${environment.apiBaseUrl}/sessions/${sessionId}/stream`, {
        method: 'GET',
        headers: { Accept: 'text/event-stream' },
        signal: controller.signal,
      })
        .then(async (response) => {
          if (!response.ok || !response.body) {
            subscriber.error(new Error(`stream request failed: ${response.status}`));
            return;
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';

          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const chunks = buffer.split('\n\n');
            buffer = chunks.pop() ?? '';

            for (const chunk of chunks) {
              const event = parseSseChunk(chunk);
              if (event) {
                subscriber.next(event);
                if (event.type === 'done' || event.type === 'error') {
                  subscriber.complete();
                  return;
                }
              }
            }
          }
          subscriber.complete();
        })
        .catch((err: unknown) => {
          if ((err as { name?: string })?.name !== 'AbortError') {
            subscriber.error(err);
          }
        });

      return () => controller.abort();
    });
  }
}

function parseSseChunk(chunk: string): DebateEvent | null {
  let eventType = '';
  let dataLine = '';

  for (const line of chunk.split('\n')) {
    if (line.startsWith('event:')) {
      eventType = line.slice('event:'.length).trim();
    } else if (line.startsWith('data:')) {
      dataLine += line.slice('data:'.length).trim();
    }
  }

  if (!eventType) return null;

  try {
    const data = dataLine ? JSON.parse(dataLine) : {};
    return { type: eventType, data } as DebateEvent;
  } catch {
    return null;
  }
}
