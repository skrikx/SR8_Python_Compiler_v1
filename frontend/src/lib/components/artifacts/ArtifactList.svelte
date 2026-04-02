<script lang="ts">
  import ArtifactCard from './ArtifactCard.svelte';
  import type { ArtifactRecord } from '$lib/api/types';

  export let artifacts: ArtifactRecord[] = [];
</script>

<section class="space-y-4">
  {#if artifacts.length}
    <div class="grid gap-4 xl:grid-cols-2">
      {#each artifacts as artifact}
        <ArtifactCard {artifact} />
      {/each}
    </div>
  {:else}
    <div class="rounded-[1.5rem] border border-dashed border-ink-300 bg-white/70 p-6 text-sm text-ink-600">
      No artifacts are indexed yet.
    </div>
  {/if}
</section>
