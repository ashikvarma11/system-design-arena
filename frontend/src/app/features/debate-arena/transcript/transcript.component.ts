import { Component, computed, input } from '@angular/core';

import { TurnBubbleComponent, TurnBubbleData } from '../turn-bubble/turn-bubble.component';

@Component({
  selector: 'app-transcript',
  standalone: true,
  imports: [TurnBubbleComponent],
  templateUrl: './transcript.component.html',
  styleUrl: './transcript.component.scss',
})
export class TranscriptComponent {
  turns = input.required<TurnBubbleData[]>();

  private readonly personaById = computed(() => {
    const map = new Map<string, string>();
    for (const turn of this.turns()) {
      map.set(turn.id, turn.persona);
    }
    return map;
  });

  rebuttalTargetPersona(turn: TurnBubbleData): string | null {
    if (!turn.critiques_turn_id) return null;
    return this.personaById().get(turn.critiques_turn_id) ?? null;
  }
}
