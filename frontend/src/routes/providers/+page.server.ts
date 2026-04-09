import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const [providers, probe] = await Promise.all([client.providers(), client.providerProbe()]);
  return {
    providers: providers.ok ? providers.data?.providers ?? [] : [],
    probes: probe.ok ? probe.data?.results ?? [] : []
  };
}
