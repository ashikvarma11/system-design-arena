import { Component, input } from '@angular/core';

import { AgreedPlan } from '../../../core/models/session.model';
import { PlanExportService } from '../../../shared/services/plan-export.service';

@Component({
  selector: 'app-agreed-plan-card',
  standalone: true,
  templateUrl: './agreed-plan-card.component.html',
  styleUrl: './agreed-plan-card.component.scss',
})
export class AgreedPlanCardComponent {
  plan = input.required<AgreedPlan>();
  title = input<string | null>(null);

  constructor(private readonly planExport: PlanExportService) {}

  download(): void {
    this.planExport.download(this.plan(), this.title());
  }
}
