<script setup lang="ts">
import type { ExplanationMode } from "../types/sudoku";

defineProps<{
  modelValue: ExplanationMode;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: ExplanationMode];
}>();

const modes: ExplanationMode[] = ["brief", "teaching", "technical"];
</script>

<template>
  <div>
    <div class="mb-2 text-sm font-medium text-slate-600">{{ $t("modes.label") }}</div>
    <div class="grid grid-cols-3 rounded-md border border-slate-300 bg-white p-1 shadow-sm">
      <button
        v-for="mode in modes"
        :key="mode"
        type="button"
        :data-testid="`mode-${mode}`"
        class="rounded px-2 py-1.5 text-sm font-medium transition"
        :class="modelValue === mode ? 'bg-emerald-700 text-white' : 'text-slate-600 hover:bg-slate-100'"
        @click="emit('update:modelValue', mode)"
      >
        {{ $t(`modes.${mode}`) }}
      </button>
    </div>
  </div>
</template>
