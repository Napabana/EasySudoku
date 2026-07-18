import { computed, reactive, ref, watch } from "vue";
import demoGrid from "../../../examples/demo_grid.json";
import type {
  CellOrigin,
  CellPosition,
  DeductionStep,
  ExplanationMode,
  Grid,
  HintResult,
  HistoryEntry,
  PersistedSession,
  UploadedImageMeta
} from "../types/sudoku";
import { getHintCell, getNextStep, solveGrid, SudokuApiError, uploadImage } from "../services/sudokuApi";
import { clearSessionStorage, clearUploadedImage, loadSession, loadUploadedImage, saveSession, saveUploadedImage } from "./usePersistence";
import { makeHistoryEntry, truncateHistory } from "./useHistory";

export const digits = [1, 2, 3, 4, 5, 6, 7, 8, 9];

export function emptyGrid(): Grid {
  return Array.from({ length: 9 }, () => Array.from({ length: 9 }, () => 0));
}

export function cloneGrid(grid: Grid): Grid {
  return grid.map((row) => [...row]);
}

export function cellKey(row: number, col: number): string {
  return `${row}-${col}`;
}

function gridCandidates(grid: Grid, row: number, col: number): number[] {
  if (grid[row][col] !== 0) return [];
  const used = new Set<number>();
  for (let i = 0; i < 9; i += 1) {
    used.add(grid[row][i]);
    used.add(grid[i][col]);
  }
  const br = Math.floor(row / 3) * 3;
  const bc = Math.floor(col / 3) * 3;
  for (let r = br; r < br + 3; r += 1) {
    for (let c = bc; c < bc + 3; c += 1) {
      used.add(grid[r][c]);
    }
  }
  return digits.filter((digit) => !used.has(digit));
}

function computeCandidates(grid: Grid): Record<string, number[]> {
  const result: Record<string, number[]> = {};
  for (let row = 0; row < 9; row += 1) {
    for (let col = 0; col < 9; col += 1) {
      result[cellKey(row, col)] = gridCandidates(grid, row, col);
    }
  }
  return result;
}

function computeConflicts(grid: Grid): Set<string> {
  const conflicts = new Set<string>();
  const addDuplicateConflicts = (cells: CellPosition[]) => {
    const byValue = new Map<number, CellPosition[]>();
    cells.forEach(({ row, col }) => {
      const value = grid[row][col];
      if (!value) return;
      byValue.set(value, [...(byValue.get(value) ?? []), { row, col }]);
    });
    byValue.forEach((positions) => {
      if (positions.length > 1) {
        positions.forEach(({ row, col }) => conflicts.add(cellKey(row, col)));
      }
    });
  };

  for (let i = 0; i < 9; i += 1) {
    addDuplicateConflicts(digits.map((col) => ({ row: i, col: col - 1 })));
    addDuplicateConflicts(digits.map((row) => ({ row: row - 1, col: i })));
  }
  for (let br = 0; br < 3; br += 1) {
    for (let bc = 0; bc < 3; bc += 1) {
      const cells: CellPosition[] = [];
      for (let r = br * 3; r < br * 3 + 3; r += 1) {
        for (let c = bc * 3; c < bc * 3 + 3; c += 1) cells.push({ row: r, col: c });
      }
      addDuplicateConflicts(cells);
    }
  }
  return conflicts;
}

function uploadErrorKey(error: unknown): string {
  if (!(error instanceof SudokuApiError)) return "errors.uploadFailed";
  const keys: Record<string, string> = {
    EMPTY_FILE: "errors.emptyFile",
    FILE_TOO_LARGE: "errors.fileTooLarge",
    OCR_MODEL_UNAVAILABLE: "errors.ocrUnavailable",
    OCR_NO_DIGITS: "errors.noDigits",
    OCR_PROCESSING_FAILED: "errors.unreadableImage",
    UNSUPPORTED_MEDIA_TYPE: "errors.invalidImageType"
  };
  return keys[error.code] ?? "errors.uploadFailed";
}

export function useSudoku() {
  const grid = ref<Grid>(emptyGrid());
  const initialGrid = ref<Grid>(emptyGrid());
  const origins = reactive<Record<string, CellOrigin>>({});
  const boardConfirmed = ref(false);
  const selectedCell = ref<CellPosition | null>(null);
  const showCandidates = ref(false);
  const explanationMode = ref<ExplanationMode>("teaching");
  const history = ref<HistoryEntry[]>([]);
  const historyCursor = ref(-1);
  const currentStep = ref<DeductionStep | null>(null);
  const hint = ref<HintResult | null>(null);
  const busy = ref(false);
  const statusKey = ref("status.ready");
  const errorMessage = ref("");
  const uploadedImage = ref<UploadedImageMeta | null>(null);
  const imageUrl = ref<string | null>(null);
  let persistenceSuspended = false;

  const candidates = computed(() => computeCandidates(grid.value));
  const conflicts = computed(() => computeConflicts(grid.value));
  const hasConflicts = computed(() => conflicts.value.size > 0);
  const canUndo = computed(() => historyCursor.value >= 0);
  const canRedo = computed(() => historyCursor.value < history.value.length - 1);

  function setOrigins(nextOrigins: Record<string, CellOrigin>): void {
    Object.keys(origins).forEach((key) => delete origins[key]);
    Object.assign(origins, nextOrigins);
  }

  function setGrid(nextGrid: Grid): void {
    grid.value = cloneGrid(nextGrid);
  }

  function selectCell(row: number, col: number): void {
    selectedCell.value = { row, col };
    hint.value = null;
  }

  function setCellValue(row: number, col: number, value: number): void {
    if (boardConfirmed.value) {
      errorMessage.value = "errors.locked";
      return;
    }
    grid.value[row][col] = value;
    const key = cellKey(row, col);
    if (value) origins[key] = origins[key] === "ocr" ? "ocr" : "user";
    else delete origins[key];
    currentStep.value = null;
  }

  async function handleUpload(file: File): Promise<void> {
    busy.value = true;
    errorMessage.value = "";
    statusKey.value = "status.uploading";
    try {
      const response = await uploadImage(file);
      setGrid(response.grid);
      const nextOrigins: Record<string, CellOrigin> = {};
      response.grid.forEach((row, r) => row.forEach((value, c) => {
        if (value) nextOrigins[cellKey(r, c)] = "ocr";
      }));
      setOrigins(nextOrigins);
      boardConfirmed.value = false;
      initialGrid.value = emptyGrid();
      history.value = [];
      historyCursor.value = -1;
      currentStep.value = null;
      showCandidates.value = true;
      uploadedImage.value = { id: "current", name: file.name, type: file.type };
      await saveUploadedImage(file);
      if (imageUrl.value) URL.revokeObjectURL(imageUrl.value);
      imageUrl.value = URL.createObjectURL(file);
      statusKey.value = "status.uploaded";
    } catch (error) {
      errorMessage.value = uploadErrorKey(error);
    } finally {
      busy.value = false;
    }
  }

  function confirmBoard(): void {
    if (hasConflicts.value) {
      errorMessage.value = "errors.solveFailed";
      return;
    }
    const nextOrigins: Record<string, CellOrigin> = {};
    grid.value.forEach((row, r) => row.forEach((value, c) => {
      if (value) nextOrigins[cellKey(r, c)] = "given";
    }));
    initialGrid.value = cloneGrid(grid.value);
    setOrigins(nextOrigins);
    boardConfirmed.value = true;
    selectedCell.value = null;
    errorMessage.value = "";
    statusKey.value = "status.confirmed";
  }

  function editBoard(): void {
    setGrid(initialGrid.value);
    const nextOrigins: Record<string, CellOrigin> = {};
    initialGrid.value.forEach((row, r) => row.forEach((value, c) => {
      if (value) nextOrigins[cellKey(r, c)] = "user";
    }));
    setOrigins(nextOrigins);
    boardConfirmed.value = false;
    history.value = [];
    historyCursor.value = -1;
    currentStep.value = null;
    hint.value = null;
    statusKey.value = "status.editing";
  }

  async function deriveNextStep(): Promise<void> {
    if (!boardConfirmed.value) {
      errorMessage.value = "errors.confirmFirst";
      return;
    }
    busy.value = true;
    errorMessage.value = "";
    statusKey.value = "status.deriving";
    const beforeGrid = cloneGrid(grid.value);
    try {
      const result = await getNextStep(beforeGrid);
      if (!result) {
        statusKey.value = "status.noStep";
        return;
      }
      setGrid(result.updatedGrid);
      if (result.step.targetCell) {
        origins[cellKey(result.step.targetCell.row, result.step.targetCell.col)] = "derived";
      }
      const activeHistory = truncateHistory(history.value, historyCursor.value);
      const entry = makeHistoryEntry(
        activeHistory.length + 1,
        beforeGrid,
        cloneGrid(result.updatedGrid),
        origins,
        computeCandidates(result.updatedGrid),
        result.step
      );
      history.value = [...activeHistory, entry];
      historyCursor.value = history.value.length - 1;
      currentStep.value = result.step;
      hint.value = null;
    } catch {
      errorMessage.value = "errors.requestFailed";
    } finally {
      busy.value = false;
    }
  }

  async function requestHint(): Promise<void> {
    if (!selectedCell.value || grid.value[selectedCell.value.row][selectedCell.value.col] !== 0) {
      errorMessage.value = "errors.invalidCell";
      return;
    }
    busy.value = true;
    errorMessage.value = "";
    statusKey.value = "status.hinting";
    try {
      hint.value = await getHintCell(grid.value, selectedCell.value.row, selectedCell.value.col);
    } catch {
      errorMessage.value = "errors.requestFailed";
    } finally {
      busy.value = false;
    }
  }

  async function solveAll(): Promise<void> {
    busy.value = true;
    errorMessage.value = "";
    statusKey.value = "status.solving";
    try {
      const result = await solveGrid(grid.value);
      if (!result.solution) {
        errorMessage.value = "errors.solveFailed";
        return;
      }
      setGrid(result.solution);
      result.solution.forEach((row, r) => row.forEach((value, c) => {
        const key = cellKey(r, c);
        if (value && !origins[key]) origins[key] = "derived";
      }));
      statusKey.value = "status.solved";
    } catch {
      errorMessage.value = "errors.requestFailed";
    } finally {
      busy.value = false;
    }
  }

  function applyHistory(index: number): void {
    const entry = history.value[index];
    if (!entry) return;
    setGrid(entry.afterGrid);
    setOrigins(entry.origins);
    currentStep.value = entry.step;
    historyCursor.value = index;
    hint.value = null;
  }

  function undo(): void {
    if (!canUndo.value) return;
    const entry = history.value[historyCursor.value];
    if (!entry) return;
    setGrid(entry.beforeGrid);
    if (historyCursor.value > 0) {
      const previous = history.value[historyCursor.value - 1];
      setOrigins(previous.origins);
      currentStep.value = previous.step;
    } else {
      const nextOrigins: Record<string, CellOrigin> = {};
      initialGrid.value.forEach((row, r) => row.forEach((value, c) => {
        if (value) nextOrigins[cellKey(r, c)] = "given";
      }));
      setOrigins(nextOrigins);
      currentStep.value = null;
    }
    historyCursor.value -= 1;
    hint.value = null;
  }

  function redo(): void {
    if (!canRedo.value) return;
    applyHistory(historyCursor.value + 1);
  }

  async function clearSession(): Promise<void> {
    persistenceSuspended = true;
    try {
      setGrid(emptyGrid());
      initialGrid.value = emptyGrid();
      setOrigins({});
      boardConfirmed.value = false;
      selectedCell.value = null;
      history.value = [];
      historyCursor.value = -1;
      currentStep.value = null;
      hint.value = null;
      uploadedImage.value = null;
      showCandidates.value = false;
      if (imageUrl.value) URL.revokeObjectURL(imageUrl.value);
      imageUrl.value = null;
      statusKey.value = "status.ready";
      errorMessage.value = "";
      await clearUploadedImage();
    } finally {
      clearSessionStorage();
      persistenceSuspended = false;
    }
  }

  async function loadDemoPuzzle(): Promise<void> {
    setGrid(demoGrid);
    initialGrid.value = emptyGrid();
    const nextOrigins: Record<string, CellOrigin> = {};
    demoGrid.forEach((row, r) => row.forEach((value, c) => {
      if (value) nextOrigins[cellKey(r, c)] = "user";
    }));
    setOrigins(nextOrigins);
    boardConfirmed.value = false;
    selectedCell.value = null;
    history.value = [];
    historyCursor.value = -1;
    currentStep.value = null;
    hint.value = null;
    uploadedImage.value = null;
    showCandidates.value = true;
    if (imageUrl.value) URL.revokeObjectURL(imageUrl.value);
    imageUrl.value = null;
    errorMessage.value = "";
    statusKey.value = "status.demoLoaded";
    await clearUploadedImage();
  }

  async function restore(): Promise<void> {
    const saved = loadSession();
    if (!saved) return;
    setGrid(saved.grid);
    initialGrid.value = saved.initialGrid;
    setOrigins(saved.origins);
    boardConfirmed.value = saved.boardConfirmed;
    selectedCell.value = saved.selectedCell;
    showCandidates.value = saved.showCandidates;
    explanationMode.value = saved.explanationMode;
    history.value = saved.history;
    historyCursor.value = saved.historyCursor;
    currentStep.value = saved.currentStep;
    uploadedImage.value = saved.uploadedImage;
    if (saved.uploadedImage) {
      const blob = await loadUploadedImage();
      if (blob) imageUrl.value = URL.createObjectURL(blob);
    }
    statusKey.value = "status.restored";
  }

  watch(
    [grid, initialGrid, boardConfirmed, selectedCell, showCandidates, explanationMode, history, historyCursor, currentStep, uploadedImage],
    () => {
      if (persistenceSuspended) return;
      const session: PersistedSession = {
        grid: grid.value,
        initialGrid: initialGrid.value,
        origins: { ...origins },
        boardConfirmed: boardConfirmed.value,
        selectedCell: selectedCell.value,
        showCandidates: showCandidates.value,
        explanationMode: explanationMode.value,
        history: history.value,
        historyCursor: historyCursor.value,
        currentStep: currentStep.value,
        uploadedImage: uploadedImage.value
      };
      saveSession(session);
    },
    { deep: true }
  );

  return {
    grid,
    initialGrid,
    origins,
    boardConfirmed,
    selectedCell,
    showCandidates,
    explanationMode,
    history,
    historyCursor,
    currentStep,
    hint,
    busy,
    statusKey,
    errorMessage,
    uploadedImage,
    imageUrl,
    candidates,
    conflicts,
    hasConflicts,
    canUndo,
    canRedo,
    selectCell,
    setCellValue,
    handleUpload,
    confirmBoard,
    editBoard,
    deriveNextStep,
    requestHint,
    solveAll,
    applyHistory,
    undo,
    redo,
    clearSession,
    loadDemoPuzzle,
    restore
  };
}
