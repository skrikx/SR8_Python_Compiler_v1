import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const artifacts = await client.artifacts();
  return {
    artifacts: artifacts.ok ? artifacts.data?.records ?? [] : [],
    error: artifacts.ok ? '' : artifacts.error ?? ''
  };
}
