<script lang="ts">
  import BenchmarkRunner from '$lib/components/benchmarks/BenchmarkRunner.svelte';
  import BenchmarkScoreTable from '$lib/components/benchmarks/BenchmarkScoreTable.svelte';
  import SelfHostingProofPanel from '$lib/components/benchmarks/SelfHostingProofPanel.svelte';
  export let data;
  export let form;

  let suite = data.suites[0] ?? '';
</script>

<div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
  <BenchmarkRunner>
    <form method="POST" class="space-y-4">
      <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Benchmarks</div>
      <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">Local performance gates</h2>
      <label class="block">
        <div class="mb-2 text-sm font-semibold text-ink-700">Suite</div>
        <select bind:value={suite} name="suite" class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm">
          <option value="">all</option>
          {#each data.suites as item}
            <option value={item}>{item}</option>
          {/each}
        </select>
      </label>
      <button class="rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-ink-50">Run suite</button>
      {#if form?.error}
        <div class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-ink-700">{form.error}</div>
      {/if}
    </form>
  </BenchmarkRunner>
  <SelfHostingProofPanel />
</div>

<div class="mt-5">
  <BenchmarkScoreTable report={form?.result ?? null} />
</div>
