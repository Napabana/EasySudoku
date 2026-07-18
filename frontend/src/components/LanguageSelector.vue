<script setup lang="ts">
import type { LocaleCode } from "../types/sudoku";

defineProps<{
  modelValue: LocaleCode;
  compact?: boolean;
}>();

const emit = defineEmits<{
  "update:modelValue": [value: LocaleCode];
}>();
</script>

<template>
  <div class="flex items-center gap-2">
    <span v-if="!compact" class="text-sm font-medium text-slate-600">{{ $t("language.label") }}</span>
    <div class="inline-flex rounded-md border border-slate-300 bg-white p-1 shadow-sm">
      <button
        type="button"
        data-testid="language-zh-CN"
        class="rounded px-3 py-1.5 text-sm font-medium transition"
        :class="modelValue === 'zh-CN' ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'"
        @click="emit('update:modelValue', 'zh-CN')"
      >
        {{ $t("language.zh") }}
      </button>
      <button
        type="button"
        data-testid="language-en-US"
        class="rounded px-3 py-1.5 text-sm font-medium transition"
        :class="modelValue === 'en-US' ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-100'"
        @click="emit('update:modelValue', 'en-US')"
      >
        {{ $t("language.en") }}
      </button>
    </div>
  </div>
</template>
