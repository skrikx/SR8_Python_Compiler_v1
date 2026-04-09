<script lang="ts">
  import type { CompileResponse } from '$lib/api/types';

  export let result: CompileResponse | null = null;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Compile result</div>
  {#if result}
    <div class="mt-4 rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
      <div class="flex items-center justify-between gap-4">
        <div>
          <div class="font-semibold text-ink-900">{result.route_contract.route_id}</div>
          <div class="mt-1 text-xs text-ink-500">{result.route_contract.summary}</div>
        </div>
        <div class="text-right text-xs text-ink-500">
          <div>{result.request_identity.auth_mode}</div>
          <div>{result.replayed ? 'replayed' : 'fresh'}</div>
        </div>
      </div>
    </div>
    {#if result.job}
      <div class="mt-4 rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
        <div class="font-semibold text-ink-900">Async job</div>
        <div class="mt-2 grid gap-2 md:grid-cols-2">
          <div>ID: {result.job.job_id}</div>
          <div>Status: {result.job.status}</div>
          <div>Attempts: {result.job.attempts}</div>
          <div>Actor: {result.job.actor_id}</div>
        </div>
      </div>
    {/if}
    {#if result.frontdoor?.status === 'intake_required'}
      <div class="mt-4 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-ink-700">
        <div class="font-semibold text-ink-900">Frontdoor intake required</div>
        <div class="mt-2 text-xs text-ink-600">Paste the completed XML back with <code>resume:</code>.</div>
        <pre class="mt-3 max-h-72 overflow-auto rounded-2xl border border-ink-200 bg-white/90 p-4 text-xs leading-6 text-ink-800">{result.frontdoor.intake_xml}</pre>
      </div>
    {:else if result.artifact}
      <div class="mt-4 grid gap-4 xl:grid-cols-2">
        <div class="space-y-4">
          <div class="rounded-2xl border border-ink-200 bg-white/90 p-4 text-sm text-ink-700">
            <div class="font-semibold text-ink-900">{result.artifact.objective}</div>
            <div class="mt-2 grid gap-2 md:grid-cols-2">
              <div>Profile: {result.artifact.profile}</div>
              <div>Readiness: {result.artifact.validation.readiness_status}</div>
              <div>Target class: {result.artifact.target_class}</div>
              <div>Source hash: {result.artifact.source.source_hash}</div>
            </div>
          </div>
          <pre class="overflow-auto rounded-2xl border border-ink-200 bg-white/90 p-4 text-xs leading-6 text-ink-800">{JSON.stringify(result.artifact, null, 2)}</pre>
        </div>
        <div class="space-y-4">
          {#if result.receipt}
            <div class="rounded-2xl border border-ink-200 bg-white/90 p-4">
              <div class="text-sm font-semibold text-ink-900">Receipt</div>
              <div class="mt-2 text-xs text-ink-600">ID: {result.receipt.receipt_id}</div>
              <div class="text-xs text-ink-600">Validation: {result.artifact.validation.readiness_status}</div>
              {#if result.receipt.notes?.length}
                <div class="mt-2 text-xs text-ink-600">{result.receipt.notes.join(' ')}</div>
              {/if}
            </div>
          {/if}
          {#if result.normalized_source}
            <div class="rounded-2xl border border-ink-200 bg-white/90 p-4">
              <div class="text-sm font-semibold text-ink-900">Normalized source</div>
              <div class="mt-2 text-xs text-ink-600">
                {result.normalized_source.source_type} - {result.normalized_source.source_hash}
              </div>
              <pre class="mt-2 overflow-auto text-xs text-ink-700">{JSON.stringify(result.normalized_source, null, 2)}</pre>
            </div>
          {/if}
          {#if result.frontdoor?.promptunit_package_xml}
            <div class="rounded-2xl border border-ink-200 bg-white/90 p-4">
              <div class="text-sm font-semibold text-ink-900">Promptunit package</div>
              <pre class="mt-2 max-h-52 overflow-auto text-xs text-ink-700">{result.frontdoor.promptunit_package_xml}</pre>
            </div>
          {/if}
        </div>
      </div>
    {:else}
      <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
        Frontdoor returned no canonical artifact yet.
      </div>
    {/if}
  {:else}
    <div class="mt-4 rounded-2xl border border-dashed border-ink-300 bg-white/70 p-4 text-sm text-ink-600">
      Submit a directive to see the compiled artifact, receipt, and normalized source here.
    </div>
  {/if}
</section>
