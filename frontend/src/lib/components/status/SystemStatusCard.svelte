<script lang="ts">
  import type { StatusSnapshot } from '$lib/api/types';

  export let status: StatusSnapshot | null = null;
  export let error = '';
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">System Status</div>
  <h2 class="mt-2 font-display text-2xl font-semibold text-ink-900">Backend readiness</h2>
  {#if status}
    <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <div class="rounded-2xl border border-ink-200 bg-white/80 p-4">
        <div class="text-xs uppercase tracking-[0.25em] text-ink-500">Status</div>
        <div class="mt-1 text-lg font-semibold">{status.status}</div>
      </div>
      <div class="rounded-2xl border border-ink-200 bg-white/80 p-4">
        <div class="text-xs uppercase tracking-[0.25em] text-ink-500">Workspace</div>
        <div class="mt-1 text-lg font-semibold">{status.workspace_path}</div>
      </div>
      <div class="rounded-2xl border border-ink-200 bg-white/80 p-4">
        <div class="text-xs uppercase tracking-[0.25em] text-ink-500">Profile</div>
        <div class="mt-1 text-lg font-semibold">{status.default_profile}</div>
      </div>
      <div class="rounded-2xl border border-ink-200 bg-white/80 p-4">
        <div class="text-xs uppercase tracking-[0.25em] text-ink-500">Adapter</div>
        <div class="mt-1 text-lg font-semibold">{status.extraction_adapter}</div>
      </div>
    </div>
  {:else}
    <div class="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-ink-700">
      {error || 'The SR8 API is not reachable right now. The shell stays usable and will fill in data when the backend is available.'}
    </div>
  {/if}
</section>
