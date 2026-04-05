import { fail } from '@sveltejs/kit';

import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const artifacts = await client.artifacts();
  return {
    artifacts: artifacts.ok ? artifacts.data?.records ?? [] : []
  };
}

export const actions = {
  default: async ({ fetch, request }) => {
    const form = await request.formData();
    const left = String(form.get('left') ?? '').trim();
    const right = String(form.get('right') ?? '').trim();
    if (!left || !right) {
      return fail(400, { error: 'Both left and right references are required.' });
    }

    const client = createApiClient(fetch, getServerApiBaseUrl());
    const result = await client.diff({ left, right });
    if (!result.ok) {
      return fail(result.status ?? 500, { error: result.error ?? 'Diff failed.' });
    }

    return { result: result.data };
  }
};
