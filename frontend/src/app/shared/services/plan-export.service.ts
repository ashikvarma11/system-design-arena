import { Injectable } from '@angular/core';

import { AgreedPlan } from '../../core/models/session.model';

@Injectable({ providedIn: 'root' })
export class PlanExportService {
  download(plan: AgreedPlan, title: string | null): void {
    const markdown = this.toMarkdown(plan, title);
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);

    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = 'plan.md';
    anchor.click();

    URL.revokeObjectURL(url);
  }

  private toMarkdown(plan: AgreedPlan, title: string | null): string {
    const section = (heading: string, items: string[]): string =>
      items.length ? `## ${heading}\n\n${items.map((i) => `- ${i}`).join('\n')}\n\n` : '';

    return (
      `# ${title ?? 'System Design Arena — Agreed Plan'}\n\n` +
      `## Decision Summary\n\n${plan.decision_summary}\n\n` +
      section('Constraints Addressed', plan.constraints_addressed) +
      section('Performance Considerations', plan.performance_considerations) +
      section('Security Considerations', plan.security_considerations) +
      section('Open Risks', plan.open_risks)
    );
  }
}
