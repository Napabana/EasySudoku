<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import ActionPanel from "./components/ActionPanel.vue";
import ConfirmDialog from "./components/ConfirmDialog.vue";
import ExplanationPanel from "./components/ExplanationPanel.vue";
import ExplanationModeSelector from "./components/ExplanationModeSelector.vue";
import HistoryPanel from "./components/HistoryPanel.vue";
import ImagePreviewModal from "./components/ImagePreviewModal.vue";
import LanguageSelector from "./components/LanguageSelector.vue";
import SudokuBoard from "./components/SudokuBoard.vue";
import { useSudoku } from "./composables/useSudoku";
import type { LocaleCode } from "./types/sudoku";

const sudoku = useSudoku();
const { locale, t } = useI18n();
const languageChosen = ref(localStorage.getItem("easysudoku.languageChosen") === "true");
const previewOpen = ref(false);
const pendingConfirm = ref<"solve" | "clear" | "branch" | null>(null);

const currentLocale = computed({
  get: () => locale.value as LocaleCode,
  set: (value: LocaleCode) => {
    locale.value = value;
    localStorage.setItem("easysudoku.locale", value);
  }
});

const targetCell = computed(() => sudoku.currentStep.value?.targetCell ?? null);
const showBusyOverlay = computed(() => {
  return sudoku.busy.value && ["status.uploading", "status.solving"].includes(sudoku.statusKey.value);
});
const filledCells = computed(() => sudoku.grid.value.flat().filter(Boolean).length);
const currentHistoryStep = computed(() => sudoku.historyCursor.value + 1);
const totalHistorySteps = computed(() => sudoku.history.value.length);
const recentEliminations = computed(() => {
  const result: Record<string, number[]> = {};
  sudoku.currentStep.value?.candidateChanges.forEach((change) => {
    result[`${change.row}-${change.col}`] = change.removed;
  });
  return result;
});
const difficultyReached = computed(() => {
  const active = sudoku.history.value.slice(0, sudoku.historyCursor.value + 1);
  const rank = ["basic", "intermediate", "advanced", "smt"];
  const max = active.reduce((current, entry) => {
    return Math.max(current, rank.indexOf(entry.step.difficulty));
  }, -1);
  return max >= 0 ? t(`difficulty.${rank[max]}`) : "-";
});

const confirmContent = computed(() => {
  if (pendingConfirm.value === "solve") {
    return {
      title: t("confirm.solveTitle"),
      body: t("confirm.solveBody"),
      confirmLabel: t("confirm.revealSolution"),
      cancelLabel: t("confirm.cancel"),
      danger: false
    };
  }
  if (pendingConfirm.value === "clear") {
    return {
      title: t("confirm.clearTitle"),
      body: t("confirm.clearBody"),
      confirmLabel: t("confirm.clearSession"),
      cancelLabel: t("confirm.cancel"),
      danger: true
    };
  }
  return {
    title: t("confirm.branchTitle"),
    body: t("confirm.branchBody"),
    confirmLabel: t("confirm.replaceHistory"),
    cancelLabel: t("confirm.cancel"),
    danger: false
  };
});

function finishLanguageChoice(): void {
  languageChosen.value = true;
  localStorage.setItem("easysudoku.languageChosen", "true");
}

function requestDeriveNextStep(): void {
  if (sudoku.historyCursor.value < sudoku.history.value.length - 1) {
    pendingConfirm.value = "branch";
    return;
  }
  void sudoku.deriveNextStep();
}

function confirmAction(): void {
  const action = pendingConfirm.value;
  pendingConfirm.value = null;
  if (action === "solve") void sudoku.solveAll();
  if (action === "clear") void sudoku.clearSession();
  if (action === "branch") void sudoku.deriveNextStep();
}

function handleGlobalKeydown(event: KeyboardEvent): void {
  const target = event.target as HTMLElement | null;
  const tag = target?.tagName.toLowerCase();
  if (tag === "input" || tag === "textarea" || tag === "select") return;
  if (pendingConfirm.value) return;
  if (event.key === "Escape" && previewOpen.value) {
    previewOpen.value = false;
    return;
  }
  if (event.key.toLowerCase() === "n") {
    event.preventDefault();
    requestDeriveNextStep();
  }
  if (event.key.toLowerCase() === "c") {
    event.preventDefault();
    sudoku.showCandidates.value = !sudoku.showCandidates.value;
  }
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    sudoku.undo();
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    sudoku.redo();
  }
}

watch(currentLocale, (value) => {
  document.documentElement.lang = value;
});

onMounted(async () => {
  document.documentElement.lang = currentLocale.value;
  await sudoku.restore();
  window.addEventListener("keydown", handleGlobalKeydown);
});

onBeforeUnmount(() => window.removeEventListener("keydown", handleGlobalKeydown));
</script>

<template>
  <div class="min-h-screen bg-paper">
    <div
      v-if="!languageChosen"
      data-testid="language-gate"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4"
    >
      <div class="w-full max-w-sm rounded-lg bg-white p-6 shadow-2xl">
        <h1 class="text-xl font-bold text-slate-900">{{ $t("app.languageFirst") }}</h1>
        <div class="mt-5">
          <LanguageSelector v-model="currentLocale" />
        </div>
        <button
          type="button"
          class="mt-6 w-full rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700"
          @click="finishLanguageChoice"
        >
          {{ $t("app.continue") }}
        </button>
      </div>
    </div>

    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex max-w-7xl flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between lg:px-6">
        <div>
          <h1 class="text-2xl font-bold tracking-normal text-slate-950">{{ $t("app.title") }}</h1>
          <p class="mt-1 text-sm text-slate-500">{{ $t("app.subtitle") }}</p>
        </div>
        <LanguageSelector v-model="currentLocale" compact />
      </div>
    </header>

    <main data-testid="app-main" class="mx-auto grid min-h-0 max-w-7xl gap-4 px-3 py-5 sm:px-4 lg:grid-cols-[minmax(420px,1fr)_320px_360px] lg:px-6">
      <section class="space-y-4">
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-base font-semibold text-slate-800">{{ $t("app.board") }}</h2>
          <div class="flex flex-wrap justify-end gap-2 text-xs text-slate-600">
            <span class="rounded bg-slate-100 px-2 py-1">{{ $t("legend.given") }}</span>
            <span class="rounded bg-blue-50 px-2 py-1 text-blue-700">{{ $t("legend.user") }}</span>
            <span class="rounded bg-emerald-50 px-2 py-1 text-emerald-700">{{ $t("legend.derived") }}</span>
            <span class="rounded bg-amber-100 px-2 py-1 text-amber-700">{{ $t("legend.target") }}</span>
          </div>
        </div>
        <SudokuBoard
          :grid="sudoku.grid.value"
          :origins="sudoku.origins"
          :selected-cell="sudoku.selectedCell.value"
          :target-cell="targetCell"
          :candidates="sudoku.candidates.value"
          :conflicts="sudoku.conflicts.value"
          :board-confirmed="sudoku.boardConfirmed.value"
          :show-candidates="sudoku.showCandidates.value"
          :recent-eliminations="recentEliminations"
          @select="sudoku.selectCell"
          @input="sudoku.setCellValue"
        />
      </section>

      <aside class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h2 class="mb-4 text-base font-semibold text-slate-800">{{ $t("app.actions") }}</h2>
        <ActionPanel
          :busy="sudoku.busy.value"
          :board-confirmed="sudoku.boardConfirmed.value"
          :show-candidates="sudoku.showCandidates.value"
          :can-undo="sudoku.canUndo.value"
          :can-redo="sudoku.canRedo.value"
          :uploaded-image="sudoku.uploadedImage.value"
          :status-key="sudoku.statusKey.value"
          :filled-cells="filledCells"
          :current-step="currentHistoryStep"
          :total-steps="totalHistorySteps"
          :difficulty-reached="difficultyReached"
          @upload="sudoku.handleUpload"
          @preview-image="previewOpen = true"
          @load-demo="sudoku.loadDemoPuzzle"
          @confirm-board="sudoku.confirmBoard"
          @edit-board="sudoku.editBoard"
          @derive-next-step="requestDeriveNextStep"
          @request-hint="sudoku.requestHint"
          @solve-all="pendingConfirm = 'solve'"
          @clear-session="pendingConfirm = 'clear'"
          @undo="sudoku.undo"
          @redo="sudoku.redo"
          @toggle-candidates="sudoku.showCandidates.value = !sudoku.showCandidates.value"
        />
      </aside>

      <aside class="min-h-0 space-y-4">
        <section class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <ExplanationModeSelector
            :model-value="sudoku.explanationMode.value"
            @update:model-value="sudoku.explanationMode.value = $event"
          />
          <div class="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-xs text-slate-600">
            <div class="mb-2 font-semibold text-slate-800">{{ $t("shortcuts.title") }}</div>
            <div class="grid grid-cols-[48px_1fr] gap-y-1">
              <span class="font-mono font-semibold text-slate-700">N</span><span>{{ $t("shortcuts.next") }}</span>
              <span class="font-mono font-semibold text-slate-700">C</span><span>{{ $t("shortcuts.candidates") }}</span>
              <span class="font-mono font-semibold text-slate-700">Esc</span><span>{{ $t("shortcuts.closePreview") }}</span>
            </div>
          </div>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 class="mb-3 text-base font-semibold text-slate-800">{{ $t("app.explanation") }}</h2>
          <ExplanationPanel
            :step="sudoku.currentStep.value"
            :hint="sudoku.hint.value"
            :mode="sudoku.explanationMode.value"
            :status-key="sudoku.statusKey.value"
            :error-message="sudoku.errorMessage.value"
          />
        </section>

        <section class="min-h-0 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 class="mb-3 text-base font-semibold text-slate-800">{{ $t("app.history") }}</h2>
          <HistoryPanel
            :history="sudoku.history.value"
            :cursor="sudoku.historyCursor.value"
            @jump="sudoku.applyHistory"
          />
        </section>
      </aside>
    </main>

    <div
      v-if="showBusyOverlay"
      data-testid="busy-overlay"
      class="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/30 p-4"
    >
      <div class="rounded-lg bg-white px-5 py-4 text-sm font-semibold text-slate-700 shadow-xl">
        {{ $t(sudoku.statusKey.value) }}
      </div>
    </div>

    <ImagePreviewModal
      v-if="previewOpen && sudoku.imageUrl.value && sudoku.uploadedImage.value"
      :image-url="sudoku.imageUrl.value"
      :file-name="sudoku.uploadedImage.value.name"
      @close="previewOpen = false"
    />

    <ConfirmDialog
      v-if="pendingConfirm"
      :title="confirmContent.title"
      :body="confirmContent.body"
      :confirm-label="confirmContent.confirmLabel"
      :cancel-label="confirmContent.cancelLabel"
      :danger="confirmContent.danger"
      @cancel="pendingConfirm = null"
      @confirm="confirmAction"
    />
  </div>
</template>
