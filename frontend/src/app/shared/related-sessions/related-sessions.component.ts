import { Component, OnInit, inject, input, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { RelatedSession } from '../../core/models/session.model';
import { SessionService } from '../../core/services/session.service';
import { PersonaBadgeComponent } from '../persona-badge/persona-badge.component';

@Component({
  selector: 'app-related-sessions',
  standalone: true,
  imports: [RouterLink, PersonaBadgeComponent],
  templateUrl: './related-sessions.component.html',
  styleUrl: './related-sessions.component.scss',
})
export class RelatedSessionsComponent implements OnInit {
  private readonly sessionService = inject(SessionService);

  sessionId = input.required<string>();

  related = signal<RelatedSession[]>([]);
  isLoading = signal(true);

  ngOnInit(): void {
    this.sessionService.related(this.sessionId()).subscribe({
      next: (results) => {
        this.related.set(results);
        this.isLoading.set(false);
      },
      error: () => {
        this.isLoading.set(false);
      },
    });
  }
}
