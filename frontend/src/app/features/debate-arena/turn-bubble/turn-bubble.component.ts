import { Component, input } from '@angular/core';

import { PersonaBadgeComponent } from '../../../shared/persona-badge/persona-badge.component';

export interface TurnBubbleData {
  id: string;
  round_number: number;
  persona: string;
  dimension: string | null;
  content: string;
  critiques_turn_id: string | null;
}

@Component({
  selector: 'app-turn-bubble',
  standalone: true,
  imports: [PersonaBadgeComponent],
  templateUrl: './turn-bubble.component.html',
  styleUrl: './turn-bubble.component.scss',
})
export class TurnBubbleComponent {
  turn = input.required<TurnBubbleData>();
  rebuttalTargetPersona = input<string | null>(null);
}
