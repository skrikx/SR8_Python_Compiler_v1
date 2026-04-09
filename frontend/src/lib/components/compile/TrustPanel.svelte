<script lang="ts">
  import type { CompileResponse, JsonObject, JsonValue } from '$lib/api/types';

  export let result: CompileResponse | null = null;

  function asRecord(value: JsonValue | null | undefined): JsonObject | null {
    return value !== null && typeof value === 'object' && !Array.isArray(value)
      ? (value as JsonObject)
      : null;
  }

  function asStringArray(value: JsonValue | null | undefined): string[] {
    return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : [];
  }

  function asBoolean(value: JsonValue | null | undefined): boolean {
    return value === true;
  }

  function asString(value: JsonValue | null | undefined): string {
    return typeof value === 'string' ? value : '';
  }

  $: metadata = result?.artifact?.metadata ?? null;
  $: trustSummary = asRecord(metadata?.extraction_trust_summary);
  $: recovery = asRecord(metadata?.weak_intent_recovery) ?? asRecord(trustSummary?.recovery);
  $: providerAssist = asRecord(metadata?.provider_assist);
  $: lowConfidenceFields = asStringArray(trustSummary?.low_confidence_fields);
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Trust</div>
  {#if result}
    <div class="mt-4 space-y-4">
      <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
        <div class="flex items-center justify-between gap-4">
          <div>
            <div class="font-semibold text-ink-900">{result.route_contract.route_id}</div>
            <div class="mt-1 text-xs text-ink-500">{result.route_contract.summary}</div>
          </div>
          <div class="text-right text-xs text-ink-500">
            <div>{result.route_contract.exposure_class}</div>
            <div>{result.route_contract.path_policy}</div>
          </div>
        </div>
      </div>

      {#if providerAssist}
        <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
          <div class="font-semibold text-ink-900">Assist extract</div>
          <div class="mt-2 grid gap-2 md:grid-cols-2">
            <div>Status: {asString(providerAssist.assist_extract_status) || 'unknown'}</div>
            <div>Route: {asString(providerAssist.assist_extract_route) || 'unknown'}</div>
            <div>Provider: {asString(providerAssist.provider) || 'unset'}</div>
            <div>Model: {asString(providerAssist.model) || 'unset'}</div>
          </div>
          {#if asString(providerAssist.error_type)}
            <div class="mt-2 text-xs text-amber-700">
              {asString(providerAssist.error_type)}: {asString(providerAssist.error_message)}
            </div>
          {/if}
        </div>
      {/if}

      {#if trustSummary || recovery}
        <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
          <div class="font-semibold text-ink-900">Weak intent recovery</div>
          <div class="mt-2 grid gap-2 md:grid-cols-2">
            <div>Replay: {result.replayed ? 'replayed' : 'fresh compile'}</div>
            <div>Intake required: {asBoolean(recovery?.intake_required) ? 'yes' : 'no'}</div>
          </div>
          {#if lowConfidenceFields.length}
            <div class="mt-3">
              <div class="text-xs uppercase tracking-[0.24em] text-ink-500">Low confidence fields</div>
              <div class="mt-2 flex flex-wrap gap-2">
                {#each lowConfidenceFields as field}
                  <span class="rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs text-amber-800">{field}</span>
                {/each}
              </div>
            </div>
          {/if}
          {#if asStringArray(recovery?.missing_fields).length || asStringArray(recovery?.weak_fields).length}
            <div class="mt-3 text-xs text-ink-600">
              Missing: {asStringArray(recovery?.missing_fields).join(', ') || 'none'}
              <br />
              Weak: {asStringArray(recovery?.weak_fields).join(', ') || 'none'}
            </div>
          {/if}
          {#if asString(recovery?.suggested_prompt)}
            <div class="mt-3 rounded-2xl border border-ink-200 bg-ink-50 px-4 py-3 text-xs text-ink-700">
              {asString(recovery?.suggested_prompt)}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
      Route contract, assist status, and weak-intent recovery appear after compile.
    </div>
  {/if}
</section>
