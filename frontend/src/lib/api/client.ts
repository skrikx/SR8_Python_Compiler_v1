import type {
  ApiResult,
  ArtifactRecord,
  BenchmarkRunReport,
  BenchmarkRunRequest,
  CompileRequest,
  CompileResponse,
  DerivativeArtifact,
  DiffRequest,
  ExtractedDimensions,
  CompilationReceiptRecord,
  IntentArtifact,
  InspectRequest,
  JsonObject,
  LintRequest,
  ProviderDescriptor,
  ProviderProbeResult,
  SettingsSnapshot,
  SourceIntent,
  StatusSnapshot,
  TransformRequest,
  TransformReceiptRecord,
  ValidateRequest,
  ValidationReport
} from './types';

export const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8000';

export type FetchLike = typeof fetch;

function joinUrl(baseUrl: string, path: string): string {
  return `${baseUrl.replace(/\/+$/, '')}${path}`;
}

async function parseResponse<T>(response: Response): Promise<ApiResult<T>> {
  const raw = await response.text();
  if (!response.ok) {
    return { ok: false, status: response.status, error: raw || response.statusText };
  }

  if (!raw) {
    return { ok: true, data: undefined as T };
  }

  try {
    return { ok: true, data: JSON.parse(raw) as T };
  } catch {
    return { ok: true, data: raw as T };
  }
}

async function request<T>(
  fetchFn: FetchLike,
  baseUrl: string,
  path: string,
  init?: RequestInit
): Promise<ApiResult<T>> {
  try {
    const response = await fetchFn(joinUrl(baseUrl, path), {
      headers: { 'content-type': 'application/json', ...(init?.headers ?? {}) },
      ...init
    });
    return await parseResponse<T>(response);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'API request failed';
    return { ok: false, error: message };
  }
}

export function createApiClient(fetchFn: FetchLike, baseUrl = DEFAULT_API_BASE_URL) {
  return {
    baseUrl,
    health: () => request<{ status: string }>(fetchFn, baseUrl, '/health'),
    status: () => request<StatusSnapshot>(fetchFn, baseUrl, '/status'),
    settings: () => request<SettingsSnapshot>(fetchFn, baseUrl, '/settings'),
    providers: () => request<ProviderDescriptor[]>(fetchFn, baseUrl, '/providers'),
    providerProbe: (provider?: string) =>
      request<{ results?: ProviderProbeResult[] } | ProviderProbeResult>(
        fetchFn,
        baseUrl,
        provider ? `/providers/probe?provider=${encodeURIComponent(provider)}` : '/providers/probe'
      ),
    artifacts: (kind?: string, profile?: string) => {
      const search = new URLSearchParams();
      if (kind) search.set('kind', kind);
      if (profile) search.set('profile', profile);
      const query = search.toString();
      return request<{ records: ArtifactRecord[] }>(
        fetchFn,
        baseUrl,
        `/artifacts${query ? `?${query}` : ''}`
      );
    },
    artifactDetail: (id: string) => request<{ record: ArtifactRecord; payload: IntentArtifact | DerivativeArtifact }>(fetchFn, baseUrl, `/artifacts/${encodeURIComponent(id)}`),
    receipts: (kind: 'compile' | 'transform' = 'compile') =>
      request<{ receipts: (CompilationReceiptRecord | TransformReceiptRecord)[] }>(
        fetchFn,
        baseUrl,
        `/receipts?kind=${kind}`
      ),
    compile: (payload: CompileRequest) =>
      request<CompileResponse>(fetchFn, baseUrl, '/compile', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    inspect: (payload: InspectRequest) =>
      request<{ artifact: IntentArtifact | DerivativeArtifact; receipt?: JsonObject; mode: string }>(
        fetchFn,
        baseUrl,
        '/inspect',
        {
          method: 'POST',
          body: JSON.stringify(payload)
        }
      ),
    validate: (payload: ValidateRequest) =>
      request<ValidationReport>(fetchFn, baseUrl, '/validate', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    transform: (payload: TransformRequest) =>
      request<DerivativeArtifact>(fetchFn, baseUrl, '/transform', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    diff: (payload: DiffRequest) =>
      request<JsonObject>(fetchFn, baseUrl, '/diff', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    lint: (payload: LintRequest) =>
      request<JsonObject>(fetchFn, baseUrl, '/lint', {
        method: 'POST',
        body: JSON.stringify(payload)
      }),
    benchmarkSuites: () => request<{ suites: string[] }>(fetchFn, baseUrl, '/benchmarks/suites'),
    benchmarkRun: (payload: BenchmarkRunRequest) =>
      request<BenchmarkRunReport>(fetchFn, baseUrl, '/benchmarks/run', {
        method: 'POST',
        body: JSON.stringify(payload)
      })
  };
}
