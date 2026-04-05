<script lang="ts">
  import type { ArtifactRecord } from '$lib/api/types';

  export let record: ArtifactRecord | null = null;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Receipt</div>
  {#if record}
    <div class="mt-4 space-y-2 text-sm text-ink-700">
      <div><span class="font-semibold text-ink-900">Record:</span> {record.record_id}</div>
      <div><span class="font-semibold text-ink-900">Artifact:</span> {record.artifact_id}</div>
      <div><span class="font-semibold text-ink-900">Path:</span> {record.file_path}</div>
    </div>
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
      Receipt metadata is not available.
    </div>
  {/if}
</section>
