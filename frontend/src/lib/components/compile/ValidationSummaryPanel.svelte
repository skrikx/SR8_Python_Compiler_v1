<script lang="ts">
  import type { ValidationReport } from '$lib/api/types';

  export let report: ValidationReport | null = null;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Validation</div>
  {#if report}
    <div class="mt-4 rounded-2xl border border-ink-200 bg-white/90 p-4">
      <div class="text-lg font-semibold text-ink-900">{report.readiness_status}</div>
      <p class="mt-2 text-sm text-ink-700">{report.summary}</p>
    </div>
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
      Validation results will appear after compile or artifact inspection.
    </div>
  {/if}
</section>
