import { Component, ElementRef, ViewChild, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import gsap from 'gsap';

import { LoadingGate } from './core/components/loading-gate/loading-gate';
import { ThemeToggleComponent } from './core/components/theme-toggle/theme-toggle.component';
import { HealthService } from './core/services/health.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, LoadingGate, ThemeToggleComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  private readonly healthService = inject(HealthService);

  readonly backendReady = signal(false);
  readonly showGate = signal(true);

  @ViewChild('gateHost', { read: ElementRef }) private gateHost?: ElementRef<HTMLElement>;
  @ViewChild('gateHost') private gate?: LoadingGate;

  constructor() {
    this.pollHealth();
  }

  onGateRetry(): void {
    this.pollHealth();
  }

  private pollHealth(): void {
    this.healthService.pollUntilHealthy().subscribe((result) => {
      if (result === 'healthy') {
        this.dismissGate();
      } else {
        this.gate?.markTimedOut();
      }
    });
  }

  private dismissGate(): void {
    this.backendReady.set(true);
    const host = this.gateHost?.nativeElement;
    if (!host) {
      this.showGate.set(false);
      return;
    }
    gsap.to(host, {
      opacity: 0,
      scale: 1.02,
      duration: 0.5,
      ease: 'power2.out',
      onComplete: () => this.showGate.set(false),
    });
  }
}
