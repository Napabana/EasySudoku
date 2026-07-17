<script setup lang="ts">
import { onBeforeUnmount, onMounted } from "vue";

defineProps<{
  imageUrl: string;
  fileName: string;
}>();

const emit = defineEmits<{
  close: [];
}>();

function handleKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape") emit("close");
}

onMounted(() => window.addEventListener("keydown", handleKeydown));
onBeforeUnmount(() => window.removeEventListener("keydown", handleKeydown));
</script>

<template>
  <div class="fixed inset-0 z-50 bg-slate-950/40 p-4" @click.self="emit('close')">
    <div class="ml-auto flex max-h-[88vh] w-full max-w-xl flex-col overflow-hidden rounded-lg bg-white shadow-2xl lg:mr-8">
      <div class="flex items-center justify-between border-b border-slate-200 px-4 py-3">
        <div class="truncate text-sm font-semibold text-slate-700">{{ fileName }}</div>
        <button
          type="button"
          class="rounded px-2 py-1 text-sm font-semibold text-slate-600 hover:bg-slate-100"
          @click="emit('close')"
        >
          {{ $t("controls.close") }}
        </button>
      </div>
      <div class="overflow-auto bg-slate-100 p-3">
        <img :src="imageUrl" :alt="fileName" class="mx-auto max-h-[72vh] max-w-full rounded bg-white object-contain" />
      </div>
    </div>
  </div>
</template>
