<script setup lang="ts">
import type { UploadedImageMeta } from "../types/sudoku";

defineProps<{
  disabled: boolean;
  uploadedImage: UploadedImageMeta | null;
}>();

const emit = defineEmits<{
  upload: [file: File];
  preview: [];
}>();

function handleChange(event: Event): void {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (file) emit("upload", file);
  input.value = "";
}
</script>

<template>
  <div class="space-y-2">
    <label class="block text-sm font-medium text-slate-600">{{ $t("controls.upload") }}</label>
    <div class="flex min-w-0 items-center gap-3">
      <label
        class="inline-flex shrink-0 cursor-pointer rounded-md bg-slate-900 px-3 py-2 text-sm font-semibold text-white hover:bg-slate-700"
        :class="disabled ? 'pointer-events-none bg-slate-300' : ''"
      >
        {{ $t("controls.chooseFile") }}
        <input
          type="file"
          accept="image/*"
          capture="environment"
          :disabled="disabled"
          class="sr-only"
          @change="handleChange"
        />
      </label>
      <button
        v-if="uploadedImage"
        type="button"
        class="min-w-0 truncate text-left text-sm font-medium text-blue-700 underline-offset-2 hover:underline"
        @click="emit('preview')"
      >
        {{ uploadedImage.name }}
      </button>
      <span v-else class="min-w-0 truncate text-sm text-slate-500">{{ $t("image.noFileSelected") }}</span>
    </div>
    <p class="text-xs text-slate-500">
      {{ uploadedImage ? $t("image.clickToPreview") : $t("image.noImage") }}
    </p>
  </div>
</template>
