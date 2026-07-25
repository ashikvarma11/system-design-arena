import { Component, OnInit, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { SessionService } from '../../../core/services/session.service';
import { SessionDetailResponse } from '../../../core/models/session.model';
import { AgreedPlanCardComponent } from '../../debate-arena/agreed-plan-card/agreed-plan-card.component';
import { TranscriptComponent } from '../../debate-arena/transcript/transcript.component';
import { RelatedSessionsComponent } from '../../../shared/related-sessions/related-sessions.component';

@Component({
  selector: 'app-history-detail',
  standalone: true,
  imports: [RouterLink, TranscriptComponent, AgreedPlanCardComponent, RelatedSessionsComponent],
  templateUrl: './history-detail.component.html',
  styleUrl: './history-detail.component.scss',
})
export class HistoryDetailComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly sessionService = inject(SessionService);

  session = signal<SessionDetailResponse | null>(null);
  isLoading = signal(true);
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    const sessionId = this.route.snapshot.paramMap.get('id') ?? '';
    this.sessionService.get(sessionId).subscribe({
      next: (session) => {
        this.session.set(session);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Could not load this session.');
        this.isLoading.set(false);
      },
    });
  }
}
