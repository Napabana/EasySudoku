import type { CellOrigin, DeductionStep, Grid, HistoryEntry } from "../types/sudoku";

export function makeHistoryEntry(
  index: number,
  beforeGrid: Grid,
  afterGrid: Grid,
  origins: Record<string, CellOrigin>,
  candidates: Record<string, number[]>,
  step: DeductionStep
): HistoryEntry {
  return {
    id: `${Date.now()}-${index}`,
    index,
    beforeGrid,
    afterGrid,
    origins: { ...origins },
    candidates,
    step,
    createdAt: new Date().toISOString()
  };
}

export function truncateHistory(history: HistoryEntry[], cursor: number): HistoryEntry[] {
  return history.slice(0, cursor + 1);
}
