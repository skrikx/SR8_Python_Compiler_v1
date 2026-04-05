<script lang="ts">
  import LintReportPanel from '$lib/components/lint/LintReportPanel.svelte';
  export let data;
  export let form;

  let artifact_ref = data.artifacts[0]?.artifact_id ?? '';
</script>

<div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
  <form method="POST" class="glass rounded-[1.75rem] p-5">
    <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Lint</div>
    <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">Quality gate</h2>
    <div class="mt-5 grid gap-4">
      <label class="block">
        <div class="mb-2 text-sm font-semibold text-ink-700">Artifact reference</div>
        <input bind:value={artifact_ref} name="artifact_ref" class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm" />
      </label>
      <button class="rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-ink-50">Run lint</button>
      {#if form?.error}
        <div class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-ink-700">{form.error}</div>
      {/if}
    </div>
  </form>
  <LintReportPanel report={form?.result ?? null} />
</div>

