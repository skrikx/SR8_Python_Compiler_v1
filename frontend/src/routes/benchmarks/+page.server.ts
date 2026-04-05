import { fail } from '@sveltejs/kit';

import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const suites = await client.benchmarkSuites();
  return {
    suites: suites.ok ? suites.data?.suites ?? [] : []
  };
}

export const actions = {
  default: async ({ fetch, request }) => {
    const form = await request.formData();
    const suite = String(form.get('suite') ?? '').trim() || null;
    const client = createApiClient(fetch, getServerApiBaseUrl());
    const result = await client.benchmarkRun({ suite });
    if (!result.ok) {
      return fail(result.status ?? 500, { error: result.error ?? 'Benchmark run failed.' });
    }
    return { result: result.data };
  }
};
