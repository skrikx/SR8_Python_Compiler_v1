<script lang="ts">
  export let workspacePath = '.sr8';
  export let apiBaseUrl = 'http://127.0.0.1:8000';
  export let available = false;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Workspace</div>
  <h2 class="mt-2 font-display text-2xl font-semibold text-ink-900">Local operating surface</h2>
  <div class="mt-4 grid gap-3 sm:grid-cols-3">
    <div class="rounded-2xl border border-ink-200 bg-white/80 p-4">
      <div class="text-xs uppercase tracking-[0.25em] text-ink-500">Workspace</div>
      <div class="mt-1 text-sm font-semibold">{workspacePath}</div>
    </div>
    <div class="rounded-2xl border border-ink-200 bg-white/80 p-4">
      <div class="text-xs uppercase tracking-[0.25em] text-ink-500">API Base</div>
      <div class="mt-1 text-sm font-semibold break-all">{apiBaseUrl}</div>
    </div>
    <div class="rounded-2xl border border-ink-200 bg-white/80 p-4">
      <div class="text-xs uppercase tracking-[0.25em] text-ink-500">Backend</div>
      <div class="mt-1 text-sm font-semibold">{available ? 'available' : 'unavailable'}</div>
    </div>
  </div>
</section>
