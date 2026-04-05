import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const [compileReceipts, transformReceipts] = await Promise.all([
    client.receipts('compile'),
    client.receipts('transform')
  ]);
  return {
    compileReceipts: compileReceipts.ok ? compileReceipts.data?.receipts ?? [] : [],
    transformReceipts: transformReceipts.ok ? transformReceipts.data?.receipts ?? [] : []
  };
}
