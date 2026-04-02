<script lang="ts">
  import type { SettingsSnapshot, StatusSnapshot } from '$lib/api/types';

  export let status: StatusSnapshot | null = null;
  export let settings: SettingsSnapshot | null = null;
</script>

<div class="flex flex-wrap items-center justify-between gap-4 rounded-[1.5rem] border border-ink-200/70 bg-white/70 px-5 py-4">
  <div>
    <div class="text-xs uppercase tracking-[0.28em] text-ink-500">Local Surface</div>
    <div class="mt-1 text-lg font-semibold text-ink-900">
      {#if status}
        {status.status === 'ok' ? 'SR8 API online' : 'SR8 API unavailable'}
      {:else}
        SR8 shell ready
      {/if}
    </div>
  </div>
  <div class="flex flex-wrap items-center gap-3 text-sm text-ink-700">
    <span class="rounded-full border border-ink-200 bg-ink-50 px-3 py-1">
      Profile: {settings?.default_profile ?? 'generic'}
    </span>
    <span class="rounded-full border border-ink-200 bg-ink-50 px-3 py-1">
      Adapter: {settings?.extraction_adapter ?? 'rule_based'}
    </span>
    <span class="rounded-full border border-moss-200 bg-moss-50 px-3 py-1 text-moss-800">
      {status?.workspace_path ?? '.sr8'}
    </span>
  </div>
</div>
