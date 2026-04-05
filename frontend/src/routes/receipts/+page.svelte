<script lang="ts">
  export let data;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Receipts</div>
  <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">Compilation and transform receipts</h2>
  <div class="mt-5 grid gap-5 xl:grid-cols-2">
    <div class="rounded-2xl border border-ink-200 bg-white/85 p-4">
      <div class="font-semibold text-ink-900">Compile receipts</div>
      <pre class="mt-3 overflow-auto text-xs text-ink-700">{JSON.stringify(data.compileReceipts, null, 2)}</pre>
    </div>
    <div class="rounded-2xl border border-ink-200 bg-white/85 p-4">
      <div class="font-semibold text-ink-900">Transform receipts</div>
      <pre class="mt-3 overflow-auto text-xs text-ink-700">{JSON.stringify(data.transformReceipts, null, 2)}</pre>
    </div>
  </div>
</section>

