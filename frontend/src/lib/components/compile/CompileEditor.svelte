<script lang="ts">
  export let value = '';
</script>

<label class="block">
  <div class="mb-2 flex items-center justify-between text-sm text-ink-700">
    <span class="font-semibold">Input editor</span>
    <span class="text-xs uppercase tracking-[0.25em] text-ink-500">source</span>
  </div>
  <textarea
    bind:value
    class="min-h-[22rem] w-full rounded-[1.5rem] border border-ink-200 bg-white/90 p-4 font-mono text-sm leading-6 text-ink-900 shadow-glow outline-none transition focus:border-moss-300 focus:ring-2 focus:ring-moss-200/70"
    placeholder="Paste a directive, PRD, plan, or canonical artifact source."
  ></textarea>
</label>
