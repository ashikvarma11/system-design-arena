import { Component, computed, input } from '@angular/core';

const PERSONA_LABELS: Record<string, string> = {
  proposer: 'Proposer',
  constraints: 'Constraints',
  performance: 'Performance',
  security: 'Security',
  critic: 'Critic',
  moderator: 'Moderator',
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
