<script setup lang="ts">
defineProps<{
  title: string;
  body: string;
  confirmLabel: string;
  cancelLabel: string;
  danger?: boolean;
}>();

const emit = defineEmits<{
  cancel: [];
  confirm: [];
}>();
</script>

<template>
  <div class="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/45 p-4" @click.self="emit('cancel')">
    <div class="w-full max-w-sm rounded-lg bg-white p-5 shadow-2xl">
      <h2 class="text-base font-semibold text-slate-950">{{ title }}</h2>
      <p class="mt-2 text-sm leading-6 text-slate-600">{{ body }}</p>
      <div class="mt-5 flex justify-end gap-2">
        <button
          type="button"
          class="h-11 rounded-md border border-slate-300 bg-white px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          @click="emit('cancel')"
        >
          {{ cancelLabel }}
        </button>
        <button
          type="button"
          class="h-11 rounded-md px-4 text-sm font-semibold text-white focus:outline-none focus:ring-2 focus:ring-offset-2"
          :class="danger ? 'bg-rose-700 hover:bg-rose-600 focus:ring-rose-500' : 'bg-blue-700 hover:bg-blue-600 focus:ring-blue-500'"
          @click="emit('confirm')"
        >
          {{ confirmLabel }}
        </button>
      </div>
    </div>
  </div>
</template>
