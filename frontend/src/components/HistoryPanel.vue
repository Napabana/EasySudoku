<script setup lang="ts">
import { nextTick, ref, watch } from "vue";
import type { HistoryEntry } from "../types/sudoku";

const props = defineProps<{
  history: HistoryEntry[];
  cursor: number;
}>();

const emit = defineEmits<{
  jump: [index: number];
}>();

const listEl = ref<HTMLElement | null>(null);

watch(
  () => [props.history.length, props.cursor],
  async () => {
    await nextTick();
    const list = listEl.value;
    const current = list?.querySelector<HTMLElement>("[data-current='true']");
    if (!list || !current) return;

    const listRect = list.getBoundingClientRect();
    const currentRect = current.getBoundingClientRect();
    const edgePadding = 2;
    if (currentRect.top < listRect.top + edgePadding) {
      list.scrollBy({ top: currentRect.top - listRect.top - edgePadding, behavior: "smooth" });
    } else if (currentRect.bottom > listRect.bottom - edgePadding) {
      list.scrollBy({ top: currentRect.bottom - listRect.bottom + edgePadding, behavior: "smooth" });
    }
  }
);
</script>

<template>
  <section data-testid="history-panel" class="flex min-h-0 flex-1 flex-col">
    <div class="mb-2 flex items-center justify-between text-sm">
      <span class="font-semibold text-slate-700">{{ $t("history.progress", { current: Math.max(cursor + 1, 0), total: history.length }) }}</span>
    </div>
    <div v-if="history.length === 0" data-testid="history-empty" class="rounded-md border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-500">
      {{ $t("history.empty") }}
    </div>
    <div
      v-else
      ref="listEl"
      data-testid="history-list"
      class="h-52 min-h-0 space-y-1.5 overflow-y-auto overflow-x-hidden pr-2 [scrollbar-gutter:stable] sm:h-56 lg:h-auto lg:flex-1"
    >
      <button
        v-for="(entry, index) in history"
        :key="entry.id"
        data-testid="history-item"
        type="button"
        class="w-full rounded-md border px-3 py-2 text-left text-sm transition focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-1"
        :class="index === cursor ? 'border-blue-500 bg-blue-50 shadow-sm' : 'border-slate-200 bg-white hover:bg-slate-50'"
        :data-current="index === cursor"
        @click="emit('jump', index)"
      >
        <div class="flex items-center justify-between gap-2 text-slate-800">
          <span class="truncate font-semibold">
            {{ $t("history.compactItem", { index: entry.index, rule: $t(`rules.${entry.step.ruleType}`) }) }}
          </span>
          <span v-if="index === cursor" class="shrink-0 text-xs font-semibold text-blue-700">{{ $t("history.current") }}</span>
        </div>
        <div v-if="entry.step.targetCell" class="mt-1 font-mono text-xs text-slate-600">
          {{ $t("history.target", {
            row: entry.step.targetCell.row + 1,
            col: entry.step.targetCell.col + 1,
            value: entry.step.value
          }) }}
        </div>
      </button>
    </div>
  </section>
</template>
