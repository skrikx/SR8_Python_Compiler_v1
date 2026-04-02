<script lang="ts">
  import type { ProviderProbeResult } from '$lib/api/types';

  export let probes: ProviderProbeResult[] = [];
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Provider probe</div>
  {#if probes.length}
    <div class="mt-4 grid gap-3 xl:grid-cols-2">
      {#each probes as probe}
        <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
          <div class="flex items-center justify-between gap-4">
            <div class="font-semibold text-ink-900">{probe.provider}</div>
            <div>{probe.available ? 'ready' : 'offline'}</div>
          </div>
          <div class="mt-2 text-xs text-ink-500">{probe.detail}</div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
      Provider probes are unavailable.
    </div>
  {/if}
</section>
