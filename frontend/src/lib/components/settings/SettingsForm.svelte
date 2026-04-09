<script lang="ts">
  import type { SettingsSnapshot } from '$lib/api/types';
  import { apiBaseUrl, workspacePath } from '$lib/stores/workspace';

  export let settings: SettingsSnapshot | null = null;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Settings</div>
  <h3 class="mt-2 font-display text-3xl font-semibold text-ink-900">Workspace controls</h3>
  <div class="mt-4 grid gap-4 xl:grid-cols-2">
    <label class="block">
      <div class="mb-2 text-sm font-semibold text-ink-700">Workspace path</div>
      <input bind:value={$workspacePath} class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm outline-none focus:border-moss-300" />
    </label>
    <label class="block">
      <div class="mb-2 text-sm font-semibold text-ink-700">API base URL</div>
      <input bind:value={$apiBaseUrl} class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm outline-none focus:border-moss-300" />
    </label>
  </div>
  {#if settings}
    <div class="mt-6 grid gap-3 xl:grid-cols-2">
      <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
        <div class="font-semibold text-ink-900">Profile</div>
        <div class="mt-1">{settings.default_profile}</div>
      </div>
      <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
        <div class="font-semibold text-ink-900">Extraction adapter</div>
        <div class="mt-1">{settings.extraction_adapter}</div>
      </div>
      <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
        <div class="font-semibold text-ink-900">Assist provider</div>
        <div class="mt-1">{settings.assist_provider ?? 'unset'}</div>
      </div>
      <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
        <div class="font-semibold text-ink-900">Assist model</div>
        <div class="mt-1">{settings.assist_model ?? 'unset'}</div>
      </div>
      <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
        <div class="font-semibold text-ink-900">Auth and rate limit</div>
        <div class="mt-1">
          {settings.api_auth_token_configured ? 'bearer-token enabled' : 'trusted-local only'}
        </div>
        <div class="mt-1">{settings.api_rate_limit_requests} requests / {settings.api_rate_limit_window_seconds}s</div>
      </div>
      <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
        <div class="font-semibold text-ink-900">Async and concurrency</div>
        <div class="mt-1">Async jobs: {settings.api_async_jobs_enabled ? 'enabled' : 'disabled'}</div>
        <div class="mt-1">Concurrent operations: {settings.api_max_concurrent_operations}</div>
      </div>
      <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
        <div class="font-semibold text-ink-900">Workspace policy</div>
        <div class="mt-1">Override: {settings.api_allow_workspace_override ? 'allowed' : 'denied'}</div>
        <div class="mt-1">Multi-tenant: {settings.api_allow_multi_tenant ? 'enabled' : 'denied'}</div>
      </div>
    </div>
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
      Settings are not available without the backend.
    </div>
  {/if}
</section>
