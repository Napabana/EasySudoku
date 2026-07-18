import type { BackendDeductionStep, DeductionStep, Grid, HintResult, LegacyStepResponse } from "../types/sudoku";

export class SudokuApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string
  ) {
    super(code);
    this.name = "SudokuApiError";
  }
}

interface UploadResponse {
  grid: Grid;
}

interface SolveResponse {
  solution: Grid | null;
}

function detectRuleType(explanation: string): string {
  if (explanation.includes("Hidden Single") || explanation.includes("隐性唯一数")) {
    return "hiddenSingle";
  }
  if (explanation.includes("Naked Pair") || explanation.includes("显性数对")) {
    return "nakedPair";
  }
  return "smtVerification";
}

function difficultyForRule(ruleType: string): DeductionStep["difficulty"] {
  if (ruleType === "hiddenSingle") return "basic";
  if (ruleType === "nakedPair") return "intermediate";
  return "smt";
}

function toFrontendRuleType(ruleType: string): string {
  const map: Record<string, string> = {
    hidden_single: "hiddenSingle",
    naked_pair: "nakedPair",
    smt_verification: "smtVerification"
  };
  return map[ruleType] ?? ruleType;
}

function toFrontendExplanationKey(ruleType: string, explanationKey: string): string {
  const byRule: Record<string, string> = {
    hiddenSingle: "explanations.hiddenSingle",
    nakedPair: "explanations.nakedPair",
    smtVerification: "explanations.smtStep"
  };
  return byRule[ruleType] ?? explanationKey.replace(/^deduction\./, "explanations.");
}

function normalizeParams(params: Record<string, string | number>): Record<string, string | number> {
  return {
    ...params,
    col: params.col ?? params.column
  };
}

export function adaptStructuredStep(step: BackendDeductionStep, rawExplanation?: string): DeductionStep {
  const ruleType = toFrontendRuleType(step.rule_type);
  return {
    ruleType,
    difficulty: step.difficulty,
    targetCell: step.target_cell,
    value: step.value,
    explanationKey: toFrontendExplanationKey(ruleType, step.explanation_key),
    explanationParams: normalizeParams(step.explanation_params),
    candidateChanges: step.candidate_changes.map((change) => ({
      row: change.row,
      col: change.col,
      removed: change.removed,
      reasonKey: change.reason_key,
      reasonParams: change.reason_params
    })),
    verificationType: step.verification_type === "human_rule" ? "human-rule" : step.verification_type,
    rawExplanation
  };
}

function candidateChangesFromEliminations(step: LegacyStepResponse): DeductionStep["candidateChanges"] {
  const removed = step.eliminations
    .map((reason) => {
      const match = reason.match(/(?:不能填|cannot be)\s*(\d)/i);
      return match ? Number(match[1]) : 0;
    })
    .filter((value) => value >= 1 && value <= 9);

  return removed.length > 0
    ? [{
        row: step.row,
        col: step.col,
        removed,
        reasonKey: "explanations.eliminatedCandidates",
        reasonParams: { count: removed.length }
      }]
    : [];
}

export function adaptLegacyStep(step: LegacyStepResponse): DeductionStep {
  const ruleType = detectRuleType(step.explanation);
  const difficulty = difficultyForRule(ruleType);
  const verificationType = difficulty === "smt" ? "smt" : "human-rule";

  return {
    ruleType,
    difficulty,
    targetCell: { row: step.row, col: step.col },
    value: step.value,
    explanationKey: ruleType === "smtVerification"
      ? "explanations.smtStep"
      : `explanations.${ruleType}`,
    explanationParams: {
      row: step.row + 1,
      col: step.col + 1,
      value: step.value,
      rule: ruleType
    },
    candidateChanges: candidateChangesFromEliminations(step),
    verificationType,
    rawExplanation: step.explanation
  };
}

function errorCode(payload: unknown): string {
  if (!payload || typeof payload !== "object" || !("detail" in payload)) return "REQUEST_FAILED";
  const detail = (payload as { detail?: unknown }).detail;
  if (detail && typeof detail === "object" && "code" in detail) {
    const code = (detail as { code?: unknown }).code;
    if (typeof code === "string" && code.length > 0) return code;
  }
  return "REQUEST_FAILED";
}

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      // A non-JSON proxy error is still represented by a stable generic code.
    }
    throw new SudokuApiError(response.status, errorCode(payload));
  }
  return response.json() as Promise<T>;
}

export async function uploadImage(file: File): Promise<UploadResponse> {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch("/upload", { method: "POST", body });
  return parseJson<UploadResponse>(response);
}

export async function getNextStep(grid: Grid): Promise<{ step: DeductionStep; updatedGrid: Grid } | null> {
  const response = await fetch("/next-step", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grid })
  });
  const data = await parseJson<LegacyStepResponse | null>(response);
  if (!data) return null;
  return {
    step: data.step
      ? adaptStructuredStep(data.step, data.legacy_explanation ?? data.explanation)
      : adaptLegacyStep(data),
    updatedGrid: data.board ?? data.updated_grid
  };
}

export async function getHintCell(grid: Grid, row: number, col: number): Promise<HintResult> {
  const response = await fetch("/hint-cell", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grid, row, col })
  });
  return parseJson<HintResult>(response);
}

export async function solveGrid(grid: Grid): Promise<SolveResponse> {
  const response = await fetch("/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ grid })
  });
  return parseJson<SolveResponse>(response);
}
