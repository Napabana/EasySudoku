<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import type { CellOrigin } from "../types/sudoku";

const props = defineProps<{
  row: number;
  col: number;
  value: number;
  origin: CellOrigin;
  candidates: number[];
  selected: boolean;
  related: boolean;
  sameBox: boolean;
  target: boolean;
  locked: boolean;
  conflict: boolean;
  sameValue: boolean;
  showCandidates: boolean;
  recentEliminations: number[];
}>();

const emit = defineEmits<{
  select: [row: number, col: number];
  input: [row: number, col: number, value: number];
  navigate: [row: number, col: number];
}>();

const { t } = useI18n();

const borderClass = computed(() => ({
  "border-l-2": props.col === 0 || props.col === 3 || props.col === 6,
  "border-r-2": props.col === 8,
  "border-t-2": props.row === 0 || props.row === 3 || props.row === 6,
  "border-b-2": props.row === 8
}));

const originClass = computed(() => {
  const classes = [];
  if (props.sameBox) classes.push("bg-indigo-50");
  else if (props.related) classes.push("bg-slate-50");
  else classes.push("bg-white");

  if (props.sameValue) classes.push("bg-cyan-50");
  if (props.origin === "given" || props.origin === "ocr") classes.push("text-slate-950 font-bold");
  if (props.origin === "user") classes.push("text-blue-800");
  if (props.origin === "derived") classes.push("text-emerald-800");
  if (props.target) classes.push("bg-amber-100 text-amber-900");
  if (props.selected) classes.push("ring-4 ring-inset ring-blue-600 z-10");
  if (props.conflict) classes.push("bg-rose-100 text-rose-800 ring-2 ring-inset ring-rose-500");
  return classes.join(" ");
});

const visibleCandidates = computed(() => {
  const values = new Set([...props.candidates, ...props.recentEliminations]);
  return Array.from(values).sort((a, b) => a - b);
});

const candidateClass = computed(() => ({
  "text-slate-700": !props.selected,
  "text-slate-950 font-bold": props.selected,
  "text-[0.68rem] sm:text-xs": true
}));

const ariaLabel = computed(() => {
  const origin = props.origin === "empty" ? t("a11y.empty") : t(`legend.${props.origin === "ocr" ? "given" : props.origin}`);
  const value = props.value ? String(props.value) : t("a11y.noValue");
  return t("a11y.cell", {
    row: props.row + 1,
    col: props.col + 1,
    value,
    origin
  });
});

function cleanValue(raw: string): number {
  const digit = raw.replace(/[^1-9]/g, "").slice(-1);
  return digit ? Number(digit) : 0;
}

function handleInput(event: Event): void {
  const target = event.target as HTMLInputElement;
  const value = cleanValue(target.value);
  emit("input", props.row, props.col, value);
  target.value = value ? String(value) : "";
}

function handleKeydown(event: KeyboardEvent): void {
  const moves: Record<string, [number, number]> = {
    ArrowUp: [Math.max(0, props.row - 1), props.col],
    ArrowDown: [Math.min(8, props.row + 1), props.col],
    ArrowLeft: [props.row, Math.max(0, props.col - 1)],
    ArrowRight: [props.row, Math.min(8, props.col + 1)]
  };
  if (event.key in moves) {
    event.preventDefault();
    const [row, col] = moves[event.key];
    emit("navigate", row, col);
    return;
  }
  if (props.locked) return;
  if (/^[1-9]$/.test(event.key)) {
    event.preventDefault();
    emit("input", props.row, props.col, Number(event.key));
  }
  if (event.key === "Backspace" || event.key === "Delete") {
    event.preventDefault();
    emit("input", props.row, props.col, 0);
  }
}
</script>

<template>
  <div
    class="relative aspect-square min-w-0 border border-slate-300 text-center transition"
    :class="[borderClass, originClass]"
    @click="emit('select', row, col)"
  >
    <input
      class="absolute inset-0 h-full w-full bg-transparent text-center text-xl font-semibold outline-none sm:text-2xl"
      :class="value ? '' : 'text-transparent caret-slate-800'"
      :value="value || ''"
      :readonly="locked"
      :aria-label="ariaLabel"
      :data-cell="`${row}-${col}`"
      inputmode="numeric"
      maxlength="1"
      autocomplete="off"
      @input="handleInput"
      @keydown="handleKeydown"
      @focus="emit('select', row, col)"
    />
    <div
      v-if="!value && showCandidates"
      class="pointer-events-none grid h-full w-full grid-cols-3 grid-rows-3 p-0.5 font-semibold leading-none sm:p-1"
      :class="candidateClass"
    >
      <span v-for="digit in 9" :key="digit" class="flex items-center justify-center">
        <span
          v-if="visibleCandidates.includes(digit)"
          :class="recentEliminations.includes(digit) ? 'candidate-removed text-rose-700 line-through decoration-2' : ''"
        >
          {{ digit }}
        </span>
      </span>
    </div>
    <div
      v-if="value && recentEliminations.length"
      class="pointer-events-none absolute inset-x-0 bottom-0 flex justify-center gap-0.5 pb-0.5 text-[0.48rem] font-semibold text-rose-700 sm:text-[0.55rem]"
      aria-hidden="true"
    >
      <span
        v-for="digit in recentEliminations"
        :key="digit"
        class="candidate-removed line-through decoration-2"
      >
        {{ digit }}
      </span>
    </div>
  </div>
</template>
