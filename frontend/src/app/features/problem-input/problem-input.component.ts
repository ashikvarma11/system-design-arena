import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { SessionService } from '../../core/services/session.service';

@Component({
  selector: 'app-problem-input',
  standalone: true,
  imports: [FormsModule, RouterLink],
  templateUrl: './problem-input.component.html',
  styleUrl: './problem-input.component.scss',
})
export class ProblemInputComponent {
  private readonly sessionService = inject(SessionService);
  private readonly router = inject(Router);

  text = signal('');
  selectedFile = signal<File | null>(null);
  isSubmitting = signal(false);
  errorMessage = signal<string | null>(null);
  isDragOver = signal(false);

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.selectedFile.set(input.files?.[0] ?? null);
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver.set(false);
    const file = event.dataTransfer?.files?.[0];
    if (file) this.selectedFile.set(file);
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.isDragOver.set(true);
  }

  onDragLeave(): void {
    this.isDragOver.set(false);
  }

  clearFile(): void {
    this.selectedFile.set(null);
  }

  submit(): void {
    const file = this.selectedFile();
    const text = this.text().trim();

    if (!file && !text) {
      this.errorMessage.set('Enter a problem description or attach a file.');
      return;
    }

    this.isSubmitting.set(true);
    this.errorMessage.set(null);

    const request$ = file
      ? this.sessionService.createFromFile(file)
      : this.sessionService.createFromText(text);

    request$.subscribe({
      next: (session) => {
        this.isSubmitting.set(false);
        this.router.navigate(['/sessions', session.id]);
      },
      error: (err: unknown) => {
        this.isSubmitting.set(false);
        this.errorMessage.set(this.extractError(err));
      },
    });
  }

  private extractError(err: unknown): string {
    const httpErr = err as { error?: { detail?: string }; message?: string };
    return httpErr?.error?.detail ?? httpErr?.message ?? 'Something went wrong. Please try again.';
  }
}
