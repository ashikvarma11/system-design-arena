import { AgreedPlanResponse } from './session.model';

export interface TurnStartData {
  persona: string;
  round_number: number;
}

export interface TurnEndData {
  id: string;
  round_number: number;
  persona: string;
  dimension: string | null;
  content: string;
  critiques_turn_id: string | null;
}

export type DoneData = { session_id: string };
export type ErrorData = { message: string };

export type DebateEvent =
  | { type: 'turn_start'; data: TurnStartData }
  | { type: 'turn_end'; data: TurnEndData }
  | { type: 'plan'; data: AgreedPlanResponse }
  | { type: 'done'; data: DoneData }
  | { type: 'error'; data: ErrorData };
