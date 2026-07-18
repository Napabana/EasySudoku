<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import type { DeductionStep, ExplanationMode, HintResult } from "../types/sudoku";

const props = defineProps<{
  step: DeductionStep | null;
  hint: HintResult | null;
  mode: ExplanationMode;
  statusKey: string;
  errorMessage: string;
}>();

const { t } = useI18n();

const ruleLabel = computed(() => {
  if (!props.step) return "";
  return t(`rules.${props.step.ruleType}`);
});

const technicalExplanation = computed(() => {
  if (!props.step) return "";
  const removedCount = props.step.candidateChanges.reduce((total, change) => total + change.removed.length, 0);
  return t("explanations.technicalStep", {
    rule: ruleLabel.value,
    difficulty: t(`difficulty.${props.step.difficulty}`),
    verification: props.step.verificationType === "smt"
      ? t("rules.smtVerification")
      : t("technical.humanRule"),
    row: props.step.targetCell ? props.step.targetCell.row + 1 : "-",
    col: props.step.targetCell ? props.step.targetCell.col + 1 : "-",
    value: props.step.value ?? "-",
    removedCount
  });
});

const explanation = computed(() => {
  if (props.errorMessage) {
    const [key, detail] = props.errorMessage.split(": ");
    return detail ? `${t(key)}: ${detail}` : t(props.errorMessage);
  }
  if (props.hint) {
    if (!props.hint.candidates.length) {
      return t("explanations.noCandidates", {
        row: props.hint.row + 1,
        col: props.hint.col + 1
      });
    }
    const candidates = props.hint.candidates.join(", ");
    return t("explanations.hintCandidates", {
      row: props.hint.row + 1,
      col: props.hint.col + 1,
      candidates
    });
  }
  if (!props.step) return t(props.statusKey) || t("explanations.intro");
  if (props.mode === "brief") return t("explanations.briefStep", props.step.explanationParams);
  if (props.mode === "technical") {
    return technicalExplanation.value;
  }
  return t(props.step.explanationKey, props.step.explanationParams);
});

const stepSummary = computed(() => {
  if (!props.step?.targetCell) return null;
  return {
    target: `R${props.step.targetCell.row + 1}C${props.step.targetCell.col + 1}`,
    row: props.step.targetCell.row + 1,
    col: props.step.targetCell.col + 1,
    value: props.step.value ?? "-",
    why: t(props.step.explanationKey, props.step.explanationParams),
    verification: props.step.verificationType === "smt"
      ? t("rules.smtVerification")
      : t("technical.humanRule")
  };
});
</script>

<template>
  <section data-testid="explanation-panel" class="space-y-3">
    <div v-if="step" class="flex flex-wrap items-center gap-2">
      <span class="rounded bg-slate-900 px-2 py-1 text-xs font-semibold text-white">{{ ruleLabel }}</span>
      <span class="rounded bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-600">
        {{ $t(`difficulty.${step.difficulty}`) }}
      </span>
      <span v-if="step.verificationType === 'smt'" class="rounded bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-700">
        {{ $t("rules.smtVerification") }}
      </span>
    </div>
    <div v-if="stepSummary && !hint" class="grid gap-3">
      <div class="grid grid-cols-2 gap-3">
        <div class="rounded-md border border-slate-200 bg-white p-3">
          <div class="text-xs font-semibold uppercase text-slate-500">{{ $t("explanationGroups.target") }}</div>
          <div class="mt-1 font-mono text-lg font-bold text-slate-900">{{ stepSummary.target }}</div>
        </div>
        <div class="rounded-md border border-slate-200 bg-white p-3">
          <div class="text-xs font-semibold uppercase text-slate-500">{{ $t("explanationGroups.conclusion") }}</div>
          <div class="mt-1 text-sm font-semibold text-slate-900">
            {{ $t("explanationGroups.placeValue", { value: stepSummary.value, target: stepSummary.target }) }}
          </div>
        </div>
      </div>
      <div class="rounded-md border border-slate-200 bg-white p-3">
        <div class="text-xs font-semibold uppercase text-slate-500">{{ $t("explanationGroups.why") }}</div>
        <div class="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{{ explanation }}</div>
      </div>
      <div class="rounded-md border border-slate-200 bg-white p-3">
        <div class="text-xs font-semibold uppercase text-slate-500">{{ $t("explanationGroups.verification") }}</div>
        <div class="mt-1 text-sm font-semibold text-slate-800">{{ stepSummary.verification }}</div>
      </div>
    </div>
    <div v-else class="min-h-40 whitespace-pre-wrap rounded-md border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-700 shadow-sm">
      {{ explanation }}
    </div>
  </section>
</template>
