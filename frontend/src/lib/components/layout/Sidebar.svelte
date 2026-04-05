<script lang="ts">
  export let active = '/';

  const navItems = [
    ['/', 'Dashboard'],
    ['/compile', 'Compile'],
    ['/artifacts', 'Artifacts'],
    ['/transforms', 'Transforms'],
    ['/diff', 'Diff'],
    ['/lint', 'Lint'],
    ['/receipts', 'Receipts'],
    ['/benchmarks', 'Benchmarks'],
    ['/providers', 'Providers'],
    ['/settings', 'Settings']
  ] as const;
</script>

<nav class="flex h-full flex-col justify-between gap-6 p-5">
  <div>
    <div class="mb-8">
      <div class="text-xs uppercase tracking-[0.35em] text-ink-500">SR8</div>
      <h1 class="mt-2 font-display text-2xl font-semibold text-ink-900">Compiler Field Guide</h1>
      <p class="mt-2 text-sm leading-6 text-ink-600">
        Local-first compiler operations, provider-aware when you ask for them.
      </p>
    </div>
    <div class="space-y-2">
      {#each navItems as [href, label]}
        <a
          href={href}
          class={`group flex items-center justify-between rounded-2xl px-4 py-3 text-sm font-medium transition hover:border-ink-200 hover:bg-white/70 hover:text-ink-900 ${
            active === href
              ? 'border border-moss-300/60 bg-moss-100/70 text-ink-900'
              : 'border border-transparent text-ink-700'
          }`}
        >
          <span>{label}</span>
          <span class="text-ink-400 transition group-hover:translate-x-0.5">↗</span>
        </a>
      {/each}
    </div>
  </div>
  <div class="rounded-2xl border border-ink-200/70 bg-white/70 p-4 text-xs leading-5 text-ink-600">
    Rule-first compilation stays the default. Provider assist is optional and visible.
  </div>
</nav>
