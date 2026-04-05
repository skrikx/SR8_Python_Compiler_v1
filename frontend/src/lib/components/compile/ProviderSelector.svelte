<script lang="ts">
  import type { ProviderDescriptor } from '$lib/api/types';

  export let value = 'rule_based';
  export let providers: ProviderDescriptor[] = [];
</script>

<label class="block">
  <div class="mb-2 text-sm font-semibold text-ink-700">Provider selector</div>
  <select
    bind:value
    class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm outline-none transition focus:border-moss-300 focus:ring-2 focus:ring-moss-200/70"
  >
    <option value="rule_based">rule_based</option>
    {#each providers as provider}
      <option value={provider.name}>{provider.label}</option>
    {/each}
  </select>
  <div class="mt-2 text-xs text-ink-500">Rule-based remains the default. Optional providers are opt-in.</div>
</label>
