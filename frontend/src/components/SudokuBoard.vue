<script setup lang="ts">
import { computed, nextTick } from "vue";
import SudokuCell from "./SudokuCell.vue";
import { cellKey } from "../composables/useSudoku";
import type { CellOrigin, CellPosition, Grid } from "../types/sudoku";

const props = defineProps<{
  grid: Grid;
  origins: Record<string, CellOrigin>;
  selectedCell: CellPosition | null;
  targetCell: CellPosition | null;
  candidates: Record<string, number[]>;
  conflicts: Set<string>;
  boardConfirmed: boolean;
  showCandidates: boolean;
  recentEliminations: Record<string, number[]>;
}>();

const emit = defineEmits<{
  select: [row: number, col: number];
  input: [row: number, col: number, value: number];
}>();

const rows = computed(() => props.grid.map((row, rowIndex) => ({ row, rowIndex })));

function originAt(row: number, col: number): CellOrigin {
  return props.origins[cellKey(row, col)] ?? "empty";
}

function isSelected(row: number, col: number): boolean {
  return props.selectedCell?.row === row && props.selectedCell.col === col;
}

function isTarget(row: number, col: number): boolean {
  return props.targetCell?.row === row && props.targetCell.col === col;
}

function isRelated(row: number, col: number): boolean {
  if (!props.selectedCell) return false;
  return props.selectedCell.row === row || props.selectedCell.col === col;
}

function isSameBox(row: number, col: number): boolean {
  if (!props.selectedCell) return false;
  return Math.floor(props.selectedCell.row / 3) === Math.floor(row / 3)
    && Math.floor(props.selectedCell.col / 3) === Math.floor(col / 3);
}

function isSameValue(row: number, col: number): boolean {
  if (!props.selectedCell) return false;
  const selectedValue = props.grid[props.selectedCell.row][props.selectedCell.col];
  return selectedValue !== 0 && props.grid[row][col] === selectedValue && !isSelected(row, col);
}

function isLocked(row: number, col: number): boolean {
  void row;
  void col;
  return props.boardConfirmed;
}

async function focusCell(row: number, col: number): Promise<void> {
  await nextTick();
  const input = document.querySelector<HTMLInputElement>(`input[data-cell="${row}-${col}"]`);
  input?.focus();
}
</script>

<template>
  <div data-testid="sudoku-board" class="mx-auto w-full max-w-[min(92vw,620px)] lg:max-w-[min(100%,calc(100dvh-170px))]">
    <div class="grid aspect-square grid-cols-9 overflow-hidden rounded border-2 border-slate-800 bg-white shadow-sm">
      <template v-for="{ row, rowIndex } in rows" :key="rowIndex">
        <SudokuCell
          v-for="(value, colIndex) in row"
          :key="`${rowIndex}-${colIndex}`"
          :row="rowIndex"
          :col="colIndex"
          :value="value"
          :origin="originAt(rowIndex, colIndex)"
          :candidates="candidates[cellKey(rowIndex, colIndex)] ?? []"
          :selected="isSelected(rowIndex, colIndex)"
          :related="isRelated(rowIndex, colIndex)"
          :same-box="isSameBox(rowIndex, colIndex)"
          :target="isTarget(rowIndex, colIndex)"
          :locked="isLocked(rowIndex, colIndex)"
          :conflict="conflicts.has(cellKey(rowIndex, colIndex))"
          :same-value="isSameValue(rowIndex, colIndex)"
          :show-candidates="showCandidates"
          :recent-eliminations="recentEliminations[cellKey(rowIndex, colIndex)] ?? []"
          @select="(row, col) => emit('select', row, col)"
          @input="(row, col, value) => emit('input', row, col, value)"
          @navigate="focusCell"
        />
      </template>
    </div>
  </div>
</template>
