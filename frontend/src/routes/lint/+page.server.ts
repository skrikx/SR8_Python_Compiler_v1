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
    const artifactRef = String(form.get('artifact_ref') ?? '').trim();
    if (!artifactRef) {
      return fail(400, { error: 'Artifact reference is required.' });
    }

    const client = createApiClient(fetch, getServerApiBaseUrl());
    const result = await client.lint({ artifact_ref: artifactRef });
    if (!result.ok) {
      return fail(result.status ?? 500, { error: result.error ?? 'Lint failed.' });
    }

    return { result: result.data };
  }
};
