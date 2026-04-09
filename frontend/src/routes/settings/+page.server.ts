import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const settings = await client.settings();
  return {
    settings: settings.ok ? settings.data?.settings ?? null : null
  };
}
