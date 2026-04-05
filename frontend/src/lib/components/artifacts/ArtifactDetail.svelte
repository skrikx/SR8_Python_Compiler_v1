<script lang="ts">
  import LineagePanel from './LineagePanel.svelte';
  import ReceiptPanel from './ReceiptPanel.svelte';
  import type { ArtifactRecord, DerivativeArtifact, IntentArtifact } from '$lib/api/types';

  export let record: ArtifactRecord | null = null;
  export let artifact: IntentArtifact | DerivativeArtifact | null = null;
</script>

<section class="grid gap-5 xl:grid-cols-[minmax(0,1.4fr)_minmax(24rem,0.8fr)]">
  <div class="glass rounded-[1.75rem] p-5">
    {#if artifact && 'artifact_id' in artifact}
      <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Artifact Detail</div>
      <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">{artifact.profile}</h2>
      <pre class="mt-4 overflow-auto rounded-2xl border border-ink-200 bg-white/90 p-4 text-xs leading-6 text-ink-800">{JSON.stringify(artifact, null, 2)}</pre>
    {:else if artifact}
      <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Derivative Detail</div>
      <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">{artifact.transform_target}</h2>
      <pre class="mt-4 overflow-auto rounded-2xl border border-ink-200 bg-white/90 p-4 text-xs leading-6 text-ink-800">{JSON.stringify(artifact, null, 2)}</pre>
    {:else}
      <div class="rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
        This artifact could not be loaded.
      </div>
    {/if}
  </div>
  <div class="space-y-5">
    <ReceiptPanel {record} />
    <LineagePanel artifact={artifact} />
  </div>
</section>
