<script setup lang="ts">
import ImageUploader from "./ImageUploader.vue";
import type { UploadedImageMeta } from "../types/sudoku";

defineProps<{
  busy: boolean;
  boardConfirmed: boolean;
  showCandidates: boolean;
  canUndo: boolean;
  canRedo: boolean;
  uploadedImage: UploadedImageMeta | null;
  statusKey: string;
  filledCells: number;
  currentStep: number;
  totalSteps: number;
  difficultyReached: string;
}>();

const emit = defineEmits<{
  upload: [file: File];
  previewImage: [];
  confirmBoard: [];
  editBoard: [];
  deriveNextStep: [];
  requestHint: [];
  solveAll: [];
  clearSession: [];
  undo: [];
  redo: [];
  toggleCandidates: [];
}>();
</script>

<template>
  <section class="space-y-4">
    <ImageUploader
      :disabled="busy"
      :uploaded-image="uploadedImage"
      @upload="emit('upload', $event)"
      @preview="emit('previewImage')"
    />

    <div class="rounded-md border border-slate-200 bg-slate-50 p-3">
      <div class="flex items-center justify-between">
        <span class="text-sm font-semibold text-slate-800">{{ $t("statusPanel.title") }}</span>
        <span
          class="rounded px-2 py-1 text-xs font-semibold"
          :class="boardConfirmed ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'"
        >
          {{ boardConfirmed ? $t("statusPanel.locked") : $t("statusPanel.editing") }}
        </span>
      </div>
      <dl class="mt-3 grid grid-cols-2 gap-x-3 gap-y-2 text-sm">
        <dt class="text-slate-500">{{ $t("statusPanel.filledCells") }}</dt>
        <dd class="text-right font-semibold text-slate-800">{{ filledCells }} / 81</dd>
        <dt class="text-slate-500">{{ $t("statusPanel.currentStep") }}</dt>
        <dd class="text-right font-semibold text-slate-800">{{ currentStep }} / {{ totalSteps }}</dd>
        <dt class="text-slate-500">{{ $t("statusPanel.difficultyReached") }}</dt>
        <dd class="text-right font-semibold text-slate-800">{{ difficultyReached }}</dd>
      </dl>
    </div>

    <div class="grid grid-cols-2 gap-2">
      <div
        class="col-span-2 flex h-11 items-center rounded-md border px-3 text-sm font-semibold"
        :class="boardConfirmed ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-slate-200 bg-slate-50 text-slate-600'"
      >
        {{ boardConfirmed ? $t("controls.puzzleLocked") : $t("controls.puzzleEditable") }}
      </div>
      <button
        type="button"
        class="h-11 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:text-slate-300"
        :disabled="busy || boardConfirmed"
        @click="emit('confirmBoard')"
      >
        {{ $t("controls.confirm") }}
      </button>
      <button
        type="button"
        class="h-11 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:text-slate-300"
        :disabled="busy || !boardConfirmed"
        @click="emit('editBoard')"
      >
        {{ $t("controls.edit") }}
      </button>
      <button
        type="button"
        class="col-span-2 h-12 rounded-md bg-blue-700 px-3 text-sm font-semibold text-white hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-slate-300"
        :disabled="busy || !boardConfirmed"
        @click="emit('deriveNextStep')"
      >
        {{ busy && statusKey === "status.deriving" ? $t("loading.analyzing") : $t("controls.nextStep") }}
      </button>
      <button
        type="button"
        class="h-11 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:text-slate-300"
        :disabled="busy"
        @click="emit('requestHint')"
      >
        {{ busy && statusKey === "status.hinting" ? $t("loading.analyzing") : $t("controls.hint") }}
      </button>
      <button
        type="button"
        class="h-11 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:text-slate-300"
        :disabled="busy"
        @click="emit('solveAll')"
      >
        {{ $t("controls.solve") }}
      </button>
      <button
        type="button"
        class="col-span-2 h-11 rounded-md border border-rose-200 bg-white px-3 text-sm font-semibold text-rose-700 hover:border-rose-400 hover:bg-rose-50 focus:outline-none focus:ring-2 focus:ring-rose-500 focus:ring-offset-2 disabled:text-slate-300"
        :disabled="busy"
        @click="emit('clearSession')"
      >
        {{ $t("controls.clear") }}
      </button>
    </div>

    <div class="grid grid-cols-3 gap-2">
      <button
        type="button"
        class="h-11 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:text-slate-300"
        :disabled="busy || !canUndo"
        @click="emit('undo')"
      >
        {{ $t("controls.undo") }}
      </button>
      <button
        type="button"
        class="h-11 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:text-slate-300"
        :disabled="busy || !canRedo"
        @click="emit('redo')"
      >
        {{ $t("controls.redo") }}
      </button>
      <button
        type="button"
        class="h-11 rounded-md border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        @click="emit('toggleCandidates')"
      >
        {{ showCandidates ? $t("controls.hideCandidates") : $t("controls.showCandidates") }}
      </button>
    </div>
  </section>
</template>
