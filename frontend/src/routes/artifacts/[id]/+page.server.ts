import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch, params }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const detail = await client.artifactDetail(params.id);
  return {
    record: detail.ok && detail.data ? detail.data.record : null,
    artifact: detail.ok && detail.data ? detail.data.payload : null,
    error: detail.ok ? '' : detail.error ?? 'Artifact unavailable'
  };
}
