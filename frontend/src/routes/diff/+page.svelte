<script lang="ts">
  import DiffRunner from '$lib/components/diff/DiffRunner.svelte';
  import DiffSummary from '$lib/components/diff/DiffSummary.svelte';
  export let data;
  export let form;

  let left = data.artifacts[0]?.artifact_id ?? '';
  let right = data.artifacts[1]?.artifact_id ?? data.artifacts[0]?.artifact_id ?? '';
</script>

<div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
  <DiffRunner>
    <form method="POST" class="space-y-4">
      <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Diff</div>
      <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">Semantic comparison</h2>
      <label class="block">
        <div class="mb-2 text-sm font-semibold text-ink-700">Left</div>
        <input bind:value={left} name="left" class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm" />
      </label>
      <label class="block">
        <div class="mb-2 text-sm font-semibold text-ink-700">Right</div>
        <input bind:value={right} name="right" class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm" />
      </label>
      <button class="rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-ink-50">Compare</button>
      {#if form?.error}
        <div class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-ink-700">{form.error}</div>
      {/if}
    </form>
  </DiffRunner>
  <DiffSummary report={form?.result?.payload ?? null} />
</div>
