import { Component, computed, input } from '@angular/core';

import { personaInitials, personaLabel } from '../../../shared/persona-badge/persona-badge.component';

export interface TurnBubbleData {
  id: string;
  round_number: number;
  persona: string;
  dimension: string | null;
  content: string;
  critiques_turn_id: string | null;
  agreement_status: string | null;
}

const RIGHT_SIDE_PERSONAS = new Set(['security', 'critic']);

@Component({
  selector: 'app-turn-bubble',
  standalone: true,
  templateUrl: './turn-bubble.component.html',
  styleUrl: './turn-bubble.component.scss',
})
export class TurnBubbleComponent {
  turn = input.required<TurnBubbleData>();
  rebuttalTargetPersona = input<string | null>(null);

  side = computed<'left' | 'right' | 'center'>(() => {
    const persona = this.turn().persona;
    if (persona === 'moderator') return 'center';
    return RIGHT_SIDE_PERSONAS.has(persona) ? 'right' : 'left';
  });

  initials = computed(() => personaInitials(this.turn().persona));
  label = computed(() => personaLabel(this.turn().persona));
}
