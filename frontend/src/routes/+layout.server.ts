import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const [status, settings, providers] = await Promise.all([
    client.status(),
    client.settings(),
    client.providers()
  ]);

  return {
    status: status.ok ? status.data : null,
    statusError: status.ok ? '' : status.error ?? 'SR8 API unavailable',
    settings: settings.ok ? settings.data?.settings ?? null : null,
    settingsError: settings.ok ? '' : settings.error ?? '',
    providers: providers.ok ? providers.data?.providers ?? [] : [],
    providersError: providers.ok ? '' : providers.error ?? ''
  };
}
