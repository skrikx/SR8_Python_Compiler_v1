<script lang="ts">
  import type { CompileResponse } from '$lib/api/types';

  export let result: CompileResponse | null = null;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Compile result</div>
  {#if result}
    <div class="mt-4 grid gap-4 xl:grid-cols-2">
      <pre class="overflow-auto rounded-2xl border border-ink-200 bg-white/90 p-4 text-xs leading-6 text-ink-800">{JSON.stringify(result.artifact, null, 2)}</pre>
      <div class="space-y-4">
        <div class="rounded-2xl border border-ink-200 bg-white/90 p-4">
          <div class="text-sm font-semibold text-ink-900">Receipt</div>
          <div class="mt-2 text-xs text-ink-600">ID: {result.receipt.receipt_id}</div>
          <div class="text-xs text-ink-600">Validation: {result.artifact.validation.readiness_status}</div>
        </div>
        <div class="rounded-2xl border border-ink-200 bg-white/90 p-4">
          <div class="text-sm font-semibold text-ink-900">Normalized source</div>
          <pre class="mt-2 overflow-auto text-xs text-ink-700">{JSON.stringify(result.normalized_source, null, 2)}</pre>
        </div>
      </div>
    </div>
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
      Submit a directive to see the compiled artifact, receipt, and normalized source here.
    </div>
  {/if}
</section>
