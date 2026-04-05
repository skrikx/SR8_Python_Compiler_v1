<script lang="ts">
  import type { BenchmarkRunReport } from '$lib/api/types';

  export let report: BenchmarkRunReport | null = null;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Score table</div>
  {#if report}
    <pre class="mt-4 overflow-auto rounded-2xl border border-ink-200 bg-white/90 p-4 text-xs leading-6 text-ink-800">{JSON.stringify(report, null, 2)}</pre>
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">Benchmark scores will appear after a run.</div>
  {/if}
</section>
