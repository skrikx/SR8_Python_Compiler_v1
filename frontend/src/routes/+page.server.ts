import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const [artifacts, receipts, suites] = await Promise.all([
    client.artifacts(),
    client.receipts('compile'),
    client.benchmarkSuites()
  ]);

  return {
    artifacts: artifacts.ok ? artifacts.data?.records ?? [] : [],
    artifactsError: artifacts.ok ? '' : artifacts.error ?? '',
    receipts: receipts.ok ? receipts.data?.receipts ?? [] : [],
    receiptsError: receipts.ok ? '' : receipts.error ?? '',
    suites: suites.ok ? suites.data?.suites ?? [] : [],
    suitesError: suites.ok ? '' : suites.error ?? ''
  };
}
