import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./features/problem-input/problem-input.component').then((m) => m.ProblemInputComponent),
  },
  {
    path: 'sessions/:id',
    loadComponent: () =>
      import('./features/debate-arena/debate-arena.component').then((m) => m.DebateArenaComponent),
  },
  {
    path: 'history',
    loadComponent: () =>
      import('./features/history/history-list/history-list.component').then((m) => m.HistoryListComponent),
  },
  {
    path: 'history/:id',
    loadComponent: () =>
      import('./features/history/history-detail/history-detail.component').then(
        (m) => m.HistoryDetailComponent,
      ),
  },
  { path: '**', redirectTo: '' },
];
