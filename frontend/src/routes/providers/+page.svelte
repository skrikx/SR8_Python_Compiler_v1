<script lang="ts">
  import ProviderList from '$lib/components/providers/ProviderList.svelte';
  import ProviderProbePanel from '$lib/components/providers/ProviderProbePanel.svelte';
  export let data;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Providers</div>
  <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">Optional mesh</h2>
  <p class="mt-3 max-w-3xl text-sm leading-6 text-ink-700">
    These providers are additive and never replace rule-first compilation. The backend reports the truth, and the UI reflects it.
  </p>
</section>

<div class="mt-5 grid gap-5 xl:grid-cols-2">
  <ProviderList providers={data.providers} />
  <ProviderProbePanel probes={data.probes} />
</div>

