<script lang="ts">
  import type { ProviderDescriptor } from '$lib/api/types';

  export let providers: ProviderDescriptor[] = [];
</script>

<section class="space-y-4">
  {#if providers.length}
    <div class="grid gap-4 xl:grid-cols-2">
      {#each providers as provider}
        <div class="rounded-[1.5rem] border border-ink-200 bg-white/85 p-4">
          <div class="flex items-center justify-between gap-4">
            <div>
              <div class="text-xs uppercase tracking-[0.25em] text-ink-500">{provider.name}</div>
              <div class="mt-1 font-semibold text-ink-900">{provider.label}</div>
            </div>
            <span class="rounded-full border border-moss-200 bg-moss-50 px-3 py-1 text-xs text-moss-800">
              {provider.supports_live_inference ? 'live' : 'probe-only'}
            </span>
          </div>
          <div class="mt-3 text-sm text-ink-700">
            Capabilities: {provider.capabilities.join(', ')}
          </div>
        </div>
      {/each}
    </div>
  {:else}
    <div class="rounded-[1.5rem] border border-dashed border-ink-300 bg-white/70 p-6 text-sm text-ink-600">
      No providers are registered.
    </div>
  {/if}
</section>
