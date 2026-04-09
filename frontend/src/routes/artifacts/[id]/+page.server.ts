import { createApiClient } from '$lib/api/client';
import { getServerApiBaseUrl } from '$lib/api/server';

export async function load({ fetch, params }) {
  const client = createApiClient(fetch, getServerApiBaseUrl());
  const detail = await client.artifactDetail(params.id);
  const record = detail.ok && detail.data ? detail.data.record : null;
  const validation =
    record && record.artifact_kind === 'canonical'
      ? await client.validate({ artifact_path: record.file_path })
      : null;

  return {
    record,
    artifact: detail.ok && detail.data ? detail.data.payload : null,
    validation: validation?.ok ? validation.data?.payload ?? null : null,
    validationRoute: validation?.ok ? validation.data?.route_contract ?? null : null,
    error: detail.ok ? '' : detail.error ?? 'Artifact unavailable'
  };
}
