<script lang="ts">
  import TransformRunner from '$lib/components/transforms/TransformRunner.svelte';
  import DerivativePreview from '$lib/components/transforms/DerivativePreview.svelte';
  export let data;
  export let form;

  let artifact_path = data.artifacts[0]?.file_path ?? '';
  let target = data.targets[0] ?? 'markdown_prd';
</script>

<div class="grid gap-5 xl:grid-cols-[minmax(0,1fr)_24rem]">
  <TransformRunner>
    <form method="POST" class="space-y-4">
      <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Transforms</div>
      <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">Derivative rendering</h2>
      <label class="block">
        <div class="mb-2 text-sm font-semibold text-ink-700">Artifact path or ID</div>
        <input bind:value={artifact_path} name="artifact_path" class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm outline-none focus:border-moss-300" />
      </label>
      <label class="block">
        <div class="mb-2 text-sm font-semibold text-ink-700">Target</div>
        <select bind:value={target} name="target" class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm">
          {#each data.targets as item}
            <option value={item}>{item}</option>
          {/each}
        </select>
      </label>
      <button class="rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-ink-50">Render derivative</button>
      {#if form?.error}
        <div class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-ink-700">{form.error}</div>
      {/if}
    </form>
  </TransformRunner>
  <DerivativePreview content={form?.result?.content ?? 'Run a transform to preview derivative content.'} />
</div>
