import { fail } from '@sveltejs/kit';

import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

const targets = ['markdown_prd', 'markdown_plan', 'markdown_prompt_pack', 'markdown_procedure', 'markdown_research_brief'];

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const artifacts = await client.artifacts();
  return {
    artifacts: artifacts.ok ? artifacts.data?.records ?? [] : [],
    targets
  };
}

export const actions = {
  default: async ({ fetch, request }) => {
    const form = await request.formData();
    const artifactPath = String(form.get('artifact_path') ?? '').trim();
    const target = String(form.get('target') ?? 'markdown_prd').trim();
    if (!artifactPath) {
      return fail(400, { error: 'Artifact path or ID is required.' });
    }

    const client = createApiClient(fetch, getServerApiBaseUrl());
    const result = await client.transform({ artifact_path: artifactPath, target });
    if (!result.ok) {
      return fail(result.status ?? 500, { error: result.error ?? 'Transform failed.' });
    }

    return { result: result.data };
  }
};
