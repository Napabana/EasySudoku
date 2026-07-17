export type Grid = number[][];
export type CellOrigin = "empty" | "ocr" | "user" | "given" | "derived";
export type ExplanationMode = "brief" | "teaching" | "technical";
export type LocaleCode = "zh-CN" | "en-US";
export type Difficulty = "basic" | "intermediate" | "advanced" | "smt";
export type VerificationType = "human-rule" | "smt";

export interface CellPosition {
  row: number;
  col: number;
}

export interface CandidateChange {
  row: number;
  col: number;
  removed: number[];
  reasonKey?: string;
  reasonParams?: Record<string, string | number>;
}

export interface DeductionStep {
  ruleType: string;
  difficulty: Difficulty;
  targetCell?: CellPosition;
  value?: number;
  explanationKey: string;
  explanationParams: Record<string, string | number>;
  candidateChanges: CandidateChange[];
  verificationType?: VerificationType;
  rawExplanation?: string;
}

export interface HistoryEntry {
  id: string;
  index: number;
  beforeGrid: Grid;
  afterGrid: Grid;
  origins: Record<string, CellOrigin>;
  candidates: Record<string, number[]>;
  step: DeductionStep;
  createdAt: string;
}

export interface UploadedImageMeta {
  id: string;
  name: string;
  type: string;
}

export interface PersistedSession {
  grid: Grid;
  initialGrid: Grid;
  origins: Record<string, CellOrigin>;
  boardConfirmed: boolean;
  selectedCell: CellPosition | null;
  showCandidates: boolean;
  explanationMode: ExplanationMode;
  history: HistoryEntry[];
  historyCursor: number;
  currentStep: DeductionStep | null;
  uploadedImage: UploadedImageMeta | null;
}

export interface HintResult {
  row: number;
  col: number;
  candidates: number[];
  eliminations: string[];
  explanation: string;
}

export interface LegacyStepResponse {
  row: number;
  col: number;
  value: number;
  explanation: string;
  eliminations: string[];
  updated_grid: Grid;
  step?: BackendDeductionStep;
  board?: Grid;
  candidates?: unknown;
  legacy_explanation?: string;
}

export interface BackendCandidateChange {
  row: number;
  col: number;
  removed: number[];
  reason_key?: string;
  reason_params?: Record<string, string | number>;
}

export interface BackendDeductionStep {
  rule_type: string;
  difficulty: Difficulty;
  target_cell?: CellPosition;
  value?: number;
  explanation_key: string;
  explanation_params: Record<string, string | number>;
  candidate_changes: BackendCandidateChange[];
  verification_type?: "human_rule" | "smt";
}
