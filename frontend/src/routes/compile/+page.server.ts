import { fail } from '@sveltejs/kit';

import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

const DEFAULT_SOURCE = `Objective: Draft a product-ready PRD for a local compiler surface.
Scope:
- Keep the compiler rule-first.
- Add optional provider assist and a local frontend.
Success Criteria:
- Outputs are visible, testable, and exportable.`;

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const [status, providers, settings] = await Promise.all([
    client.status(),
    client.providers(),
    client.settings()
  ]);

  return {
    source: DEFAULT_SOURCE,
    status: status.ok ? status.data : null,
    providers: providers.ok ? providers.data?.providers ?? [] : [],
    settings: settings.ok ? settings.data?.settings ?? null : null
  };
}

export const actions = {
  default: async ({ fetch, request }) => {
    const form = await request.formData();
    const source = String(form.get('source') ?? '').trim();
    const profile = String(form.get('profile') ?? 'generic').trim() || 'generic';
    const sourceType = String(form.get('source_type') ?? '').trim() || null;
    const ruleOnly = String(form.get('rule_only') ?? '') === 'on';
    const assistProvider = String(form.get('assist_provider') ?? '').trim() || null;
    const assistModel = String(form.get('assist_model') ?? '').trim() || null;
    const asyncMode = String(form.get('async_mode') ?? '') === 'on';
    const idempotencyKey = String(form.get('idempotency_key') ?? '').trim() || null;

    if (!source) {
      return fail(400, { error: 'Source is required.' });
    }

    const client = createApiClient(fetch, getServerApiBaseUrl());
    const result = await client.compile({
      source,
      profile,
      source_type: sourceType,
      rule_only: ruleOnly,
      assist_provider: assistProvider,
      assist_model: assistModel,
      async_mode: asyncMode,
      idempotency_key: idempotencyKey
    });

    if (!result.ok) {
      return fail(result.status ?? 500, { error: result.error ?? 'Compile failed.' });
    }

    return { result: result.data };
  }
};
