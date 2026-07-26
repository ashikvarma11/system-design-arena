import { Injectable, effect, signal } from '@angular/core';

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'sda-theme';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly theme = signal<Theme>(this.readInitial());

  constructor() {
    effect(() => this.apply(this.theme()));
  }

  toggle(): void {
    this.theme.set(this.theme() === 'dark' ? 'light' : 'dark');
  }

  private readInitial(): Theme {
    const fromDom = document.documentElement.getAttribute('data-theme');
    if (fromDom === 'light' || fromDom === 'dark') {
      return fromDom;
    }
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
    if (typeof window.matchMedia !== 'function') {
      return 'light';
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  private apply(theme: Theme): void {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
  }
}
