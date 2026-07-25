export interface ProblemBrief {
  goals: string[];
  constraints: string[];
  non_goals: string[];
}

export type SessionStatus = 'brief_created' | 'debating' | 'completed' | 'failed';

export interface SessionResponse {
  id: string;
  created_at: string;
  status: SessionStatus;
  input_type: string;
  raw_input_filename: string | null;
  problem_brief_json: ProblemBrief | null;
  rounds_planned: number;
  title: string | null;
}

export interface SessionListItem {
  id: string;
  created_at: string;
  status: SessionStatus;
  title: string | null;
}

export interface TurnResponse {
  id: string;
  session_id: string;
  round_number: number;
  persona: string;
  dimension: string | null;
  content: string;
  critiques_turn_id: string | null;
  retrieved_concept_ids: string[] | null;
  created_at: string;
}

export interface AgreedPlan {
  decision_summary: string;
  constraints_addressed: string[];
  performance_considerations: string[];
  security_considerations: string[];
  open_risks: string[];
}

export interface AgreedPlanResponse extends AgreedPlan {
  id: string;
  session_id: string;
  created_at: string;
}

export interface SessionDetailResponse extends SessionResponse {
  turns: TurnResponse[];
  agreed_plan: AgreedPlanResponse | null;
}

export interface RelatedSession {
  session_id: string;
  title: string | null;
  status: SessionStatus;
  score: number;
  matched_persona: string | null;
  matched_snippet: string | null;
}
