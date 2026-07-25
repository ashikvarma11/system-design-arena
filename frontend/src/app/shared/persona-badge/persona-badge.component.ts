import { Component, computed, input } from '@angular/core';

const PERSONA_LABELS: Record<string, string> = {
  proposer: 'Proposer',
  constraints: 'Constraints',
  performance: 'Performance',
  security: 'Security',
  critic: 'Critic',
  moderator: 'Moderator',
};

const PERSONA_INITIALS: Record<string, string> = {
  proposer: 'PR',
  constraints: 'CN',
  performance: 'PF',
  security: 'SC',
  critic: 'CR',
  moderator: 'MD',
};

@Component({
  selector: 'app-persona-badge',
  standalone: true,
  template: `<span class="badge" [class]="'badge--' + persona()">{{ label() }}</span>`,
  styleUrl: './persona-badge.component.scss',
})
export class PersonaBadgeComponent {
  persona = input.required<string>();
  label = computed(() => PERSONA_LABELS[this.persona()] ?? this.persona());
}

export function personaInitials(persona: string): string {
  return PERSONA_INITIALS[persona] ?? persona.slice(0, 2).toUpperCase();
}

export function personaLabel(persona: string): string {
  return PERSONA_LABELS[persona] ?? persona;
}
