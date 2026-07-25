import { Component, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Subscription } from 'rxjs';

import { DebateStreamService } from '../../core/services/debate-stream.service';
import { SessionService } from '../../core/services/session.service';
import { AgreedPlanResponse, SessionDetailResponse } from '../../core/models/session.model';
import { AgreedPlanCardComponent } from './agreed-plan-card/agreed-plan-card.component';
import { TranscriptComponent } from './transcript/transcript.component';
import { TurnBubbleData } from './turn-bubble/turn-bubble.component';
import { RelatedSessionsComponent } from '../../shared/related-sessions/related-sessions.component';

@Component({
  selector: 'app-debate-arena',
  standalone: true,
  imports: [TranscriptComponent, AgreedPlanCardComponent, RelatedSessionsComponent, RouterLink],
  templateUrl: './debate-arena.component.html',
  styleUrl: './debate-arena.component.scss',
})
export class DebateArenaComponent implements OnInit, OnDestroy {
  private readonly route = inject(ActivatedRoute);
  private readonly sessionService = inject(SessionService);
  private readonly debateStream = inject(DebateStreamService);
  private streamSub: Subscription | null = null;

  sessionId = '';
  title = signal<string | null>(null);
  turns = signal<TurnBubbleData[]>([]);
  plan = signal<AgreedPlanResponse | null>(null);
  activePersona = signal<string | null>(null);
  status = signal<'loading' | 'streaming' | 'completed' | 'failed'>('loading');
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    this.sessionId = this.route.snapshot.paramMap.get('id') ?? '';
    this.loadSession();
  }

  ngOnDestroy(): void {
    this.streamSub?.unsubscribe();
  }

  private loadSession(): void {
    this.sessionService.get(this.sessionId).subscribe({
      next: (session) => {
        this.title.set(session.title);
        this.turns.set(session.turns.map(toTurnBubbleData));
        this.plan.set(session.agreed_plan);

        if (session.status === 'completed') {
          this.status.set('completed');
        } else if (session.status === 'failed') {
          this.status.set('failed');
          this.errorMessage.set('This debate previously failed. You can start a new one.');
        } else {
          this.startStream();
        }
      },
      error: () => {
        this.status.set('failed');
        this.errorMessage.set('Could not load this session.');
      },
    });
  }

  private startStream(): void {
    this.status.set('streaming');
    this.streamSub = this.debateStream.stream(this.sessionId).subscribe({
      next: (event) => {
        switch (event.type) {
          case 'turn_start':
            this.activePersona.set(event.data.persona);
            break;
          case 'turn_end':
            this.activePersona.set(null);
            this.turns.update((current) => [...current, toTurnBubbleData(event.data)]);
            break;
          case 'plan':
            this.plan.set(event.data);
            break;
          case 'done':
            this.status.set('completed');
            break;
          case 'error':
            this.status.set('failed');
            this.errorMessage.set(event.data.message);
            break;
        }
      },
      error: () => {
        this.status.set('failed');
        this.errorMessage.set('Connection to the debate stream was lost.');
      },
    });
  }
}

function toTurnBubbleData(turn: {
  id: string;
  round_number: number;
  persona: string;
  dimension: string | null;
  content: string;
  critiques_turn_id: string | null;
}): TurnBubbleData {
  return {
    id: turn.id,
    round_number: turn.round_number,
    persona: turn.persona,
    dimension: turn.dimension,
    content: turn.content,
    critiques_turn_id: turn.critiques_turn_id,
  };
}
