<script lang="ts">
  import type { ExtractedDimensions } from '$lib/api/types';

  export let extracted: ExtractedDimensions | null = null;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Confidence</div>
  {#if extracted}
    <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      {#each Object.entries(extracted) as [key, value]}
        <div class="rounded-2xl border border-ink-200 bg-white/90 p-4">
          <div class="text-xs uppercase tracking-[0.24em] text-ink-500">{key}</div>
          <div class="mt-2 text-sm text-ink-800">{JSON.stringify(value)}</div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
      Confidence signals appear after a compile result is available.
    </div>
  {/if}
</section>
