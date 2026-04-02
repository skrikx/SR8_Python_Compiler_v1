<script lang="ts">
  import type { DerivativeArtifact, IntentArtifact } from '$lib/api/types';

  export let artifact: IntentArtifact | DerivativeArtifact | null = null;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Lineage</div>
  {#if artifact && 'lineage' in artifact}
    <pre class="mt-4 overflow-auto rounded-2xl border border-ink-200 bg-white/90 p-4 text-xs leading-6 text-ink-800">{JSON.stringify(artifact.lineage, null, 2)}</pre>
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
      No lineage available.
    </div>
  {/if}
</section>
