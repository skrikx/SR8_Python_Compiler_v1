<script lang="ts">
  import CompileEditor from '$lib/components/compile/CompileEditor.svelte';
  import ProfileSelector from '$lib/components/compile/ProfileSelector.svelte';
  import ProviderSelector from '$lib/components/compile/ProviderSelector.svelte';
  import CompileResultPanel from '$lib/components/compile/CompileResultPanel.svelte';
  import ConfidencePanel from '$lib/components/compile/ConfidencePanel.svelte';
  import ValidationSummaryPanel from '$lib/components/compile/ValidationSummaryPanel.svelte';
  import type { CompileResponse, ProviderDescriptor } from '$lib/api/types';

  export let data;
  export let form: { result?: CompileResponse; error?: string } | undefined;

  const profiles = ['generic', 'prd', 'plan', 'procedure', 'prompt_pack', 'research_brief', 'whitepaper_outline', 'code_task_graph', 'repo_audit'];
  let source = data.source;
  let profile = data.settings?.default_profile ?? 'generic';
  let source_type = 'markdown';
  let rule_only = true;
  let assist_provider = data.settings?.assist_provider ?? '';
  let assist_model = data.settings?.assist_model ?? '';
  let providers: ProviderDescriptor[] = data.providers;
</script>

<div class="grid gap-5 xl:grid-cols-[minmax(0,1.1fr)_minmax(26rem,0.9fr)]">
  <form method="POST" class="glass rounded-[1.75rem] p-5">
    <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Compile</div>
    <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">Rule-first by default</h2>
    <div class="mt-5 grid gap-4">
      <CompileEditor bind:value={source} />
      <div class="grid gap-4 md:grid-cols-2">
        <ProfileSelector bind:value={profile} options={profiles} />
        <label class="block">
          <div class="mb-2 text-sm font-semibold text-ink-700">Source type</div>
          <select bind:value={source_type} class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm">
            <option value="markdown">markdown</option>
            <option value="text">text</option>
            <option value="json">json</option>
            <option value="yaml">yaml</option>
          </select>
        </label>
      </div>
      <div class="grid gap-4 md:grid-cols-2">
        <label class="block rounded-2xl border border-ink-200 bg-white/80 p-4 text-sm text-ink-700">
          <input bind:checked={rule_only} type="checkbox" name="rule_only" class="mr-2 align-middle" />
          Force rule-only mode
        </label>
        <ProviderSelector bind:value={assist_provider} providers={providers} />
      </div>
      <label class="block">
        <div class="mb-2 text-sm font-semibold text-ink-700">Assist model</div>
        <input bind:value={assist_model} class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm outline-none focus:border-moss-300" placeholder="e.g. gpt-5-mini" />
      </label>
      <input type="hidden" name="source" bind:value={source} />
      <input type="hidden" name="profile" bind:value={profile} />
      <input type="hidden" name="source_type" bind:value={source_type} />
      <input type="hidden" name="assist_provider" bind:value={assist_provider} />
      <input type="hidden" name="assist_model" bind:value={assist_model} />
      <div class="flex items-center gap-3">
        <button class="rounded-full bg-ink-900 px-5 py-3 text-sm font-semibold text-ink-50 transition hover:bg-moss-700">
          Compile
        </button>
        <span class="text-sm text-ink-600">Backend response only, no local simulation.</span>
      </div>
      {#if form?.error}
        <div class="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-ink-700">{form.error}</div>
      {/if}
    </div>
  </form>

  <div class="space-y-5">
    <ValidationSummaryPanel report={form?.result?.artifact?.validation ?? null} />
    <ConfidencePanel extracted={form?.result?.extracted_dimensions ?? null} />
  </div>
</div>

<div class="mt-5 grid gap-5 xl:grid-cols-2">
  <CompileResultPanel result={form?.result ?? null} />
  <div class="glass rounded-[1.75rem] p-5">
    <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Provider awareness</div>
    <div class="mt-4 text-sm text-ink-700">
      {#if providers.length}
        <ul class="space-y-2">
          {#each providers as provider}
            <li class="rounded-2xl border border-ink-200 bg-white/80 px-4 py-3">
              <span class="font-semibold text-ink-900">{provider.label}</span>
              <span class="ml-2 text-ink-600">({provider.name})</span>
            </li>
          {/each}
        </ul>
      {:else}
        No providers are currently registered by the backend.
      {/if}
    </div>
  </div>
</div>
