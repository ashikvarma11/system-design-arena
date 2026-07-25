import { DatePipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';

import { SessionService } from '../../../core/services/session.service';
import { SessionListItem } from '../../../core/models/session.model';

@Component({
  selector: 'app-history-list',
  standalone: true,
  imports: [RouterLink, DatePipe],
  templateUrl: './history-list.component.html',
  styleUrl: './history-list.component.scss',
})
export class HistoryListComponent implements OnInit {
  private readonly sessionService = inject(SessionService);

  sessions = signal<SessionListItem[]>([]);
  isLoading = signal(true);
  errorMessage = signal<string | null>(null);

  ngOnInit(): void {
    this.sessionService.list().subscribe({
      next: (sessions) => {
        this.sessions.set(sessions);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('Could not load debate history.');
        this.isLoading.set(false);
      },
    });
  }
}
