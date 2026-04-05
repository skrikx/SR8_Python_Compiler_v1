export type JsonValue = string | number | boolean | null | JsonObject | JsonValue[];
export interface JsonObject {
  [key: string]: JsonValue;
}

export interface ApiResult<T> {
  ok: boolean;
  data?: T;
  error?: string;
  status?: number;
}

export interface ProviderDescriptor {
  name: string;
  label: string;
  capabilities: string[];
  required_env_vars: string[];
  supports_live_inference: boolean;
  optional: boolean;
}

export interface ProviderProbeResult {
  provider: string;
  configured: boolean;
  available: boolean;
  supports_live_inference: boolean;
  missing_env_vars: string[];
  detail: string;
  capabilities: string[];
}

export interface SettingsSnapshot {
  default_profile: string;
  extraction_adapter: string;
  assist_provider: string | null;
  assist_model: string | null;
  assist_fallback_to_rule_based: boolean;
  include_raw_source: boolean;
  workspace_path: string;
}

export interface StatusSnapshot {
  status: string;
  workspace_path: string;
  default_profile: string;
  extraction_adapter: string;
  providers: ProviderProbeResult[];
  benchmark_suites: string[];
}

export interface SourceIntent {
  source_id: string;
  source_type: string;
  raw_content: string;
  normalized_content: string;
  source_hash: string;
  origin?: string | null;
  metadata: JsonObject;
}

export interface ExtractedDimensions {
  objective: string;
  scope: string[];
  exclusions: string[];
  constraints: string[];
  context_package: string[];
  assumptions: string[];
  dependencies: string[];
  success_criteria: string[];
  output_contract: string[];
  target_class: string;
  authority_context: string;
  governance_flags: {
    ambiguous: boolean;
    incomplete: boolean;
    requires_human_review: boolean;
  };
}

export interface ValidationFinding {
  rule_id: string;
  severity: string;
  message: string;
  artifact_field: string;
  suggested_fix: string;
}

export interface ValidationReport {
  report_id: string;
  readiness_status: string;
  summary: string;
  errors?: ValidationFinding[];
  warnings?: ValidationFinding[];
}

export interface LineageStep {
  stage: string;
  detail: string;
}

export interface Lineage {
  compile_run_id: string;
  pipeline_version: string;
  source_hash: string;
  parent_artifact_ids?: string[];
  steps: LineageStep[];
}

export interface IntentArtifact {
  artifact_id: string;
  artifact_version: string;
  compiler_version: string;
  profile: string;
  created_at: string;
  source: {
    source_id: string;
    source_type: string;
    source_hash: string;
    origin?: string | null;
  };
  objective: string;
  scope: string[];
  exclusions: string[];
  constraints: string[];
  context_package: string[];
  target_class: string;
  authority_context: string;
  dependencies: string[];
  assumptions: string[];
  success_criteria: string[];
  output_contract: string[];
  governance_flags: {
    ambiguous: boolean;
    incomplete: boolean;
    requires_human_review: boolean;
  };
  validation: ValidationReport;
  lineage: Lineage;
  metadata: JsonObject;
}

export interface DerivativeArtifact {
  derivative_id: string;
  parent_artifact_id: string;
  transform_target: string;
  profile: string;
  created_at: string;
  content: string;
  metadata: JsonObject;
  lineage: {
    parent_artifact_id: string;
    parent_source_hash: string;
    steps: string[];
  };
}

export interface ArtifactRecord {
  record_id: string;
  artifact_id: string;
  artifact_kind: 'canonical' | 'derivative';
  profile: string;
  target_class: string;
  transform_target?: string | null;
  source_hash: string;
  created_at: string;
  file_path: string;
  parent_artifact_id?: string | null;
  readiness_status: string;
}

export interface CompilationReceiptRecord {
  receipt_id: string;
  artifact_id: string;
  compiler_version: string;
  source_hash: string;
  profile: string;
  target_class: string;
  created_at: string;
  extracted_dimensions_summary: JsonObject;
  extraction_trust_summary: JsonObject;
  lineage_summary: JsonObject;
  validation_summary: string;
  warnings: string[];
  output_path: string;
}

export interface GovernanceDecision {
  status: 'allow' | 'deny' | 'safe_alternative_compile';
  reason: string;
  notes: string[];
}

export interface FrontdoorCompileResult {
  status: 'compiled' | 'intake_required' | 'safe_alternative';
  entry_mode: string;
  artifact_family: string;
  delivery_target: string;
  governance: GovernanceDecision;
  intake_xml?: string | null;
  promptunit_package_xml?: string | null;
  sr8_prompt_xml?: string | null;
  safe_alternative_package_xml?: string | null;
}

export interface TransformReceiptRecord {
  receipt_id: string;
  parent_artifact_id: string;
  derivative_id: string;
  transform_target: string;
  profile: string;
  created_at: string;
  renderer_version: string;
  output_path: string;
}

export interface CompileResponse {
  frontdoor?: FrontdoorCompileResult | null;
  artifact?: IntentArtifact | null;
  receipt?: CompilationReceiptRecord | null;
  normalized_source?: SourceIntent | null;
  extracted_dimensions?: ExtractedDimensions | null;
}

export interface CompileRequest {
  source: string;
  profile: string;
  source_type?: string | null;
  rule_only?: boolean;
  assist_provider?: string | null;
  assist_model?: string | null;
}

export interface ValidateRequest {
  artifact_path: string;
  profile?: string | null;
}

export interface TransformRequest {
  artifact_path: string;
  target: string;
}

export interface DiffRequest {
  left: string;
  right: string;
  workspace_path?: string;
}

export interface LintRequest {
  artifact_ref: string;
  workspace_path?: string;
}

export interface InspectRequest {
  target: string;
  workspace_path?: string;
}

export interface BenchmarkRunRequest {
  suite?: string | null;
  out_dir?: string;
}

export interface BenchmarkCaseResult {
  case_id: string;
  passed: boolean;
  aggregate_score: number;
  readiness_status: string;
  failure_clusters: string[];
}

export interface BenchmarkRunReport {
  run_id: string;
  suite: string;
  compiler_version: string;
  rubric_id: string;
  results: BenchmarkCaseResult[];
  summary: {
    suite: string;
    total_cases: number;
    passed_cases: number;
    failed_cases: number;
    average_score: number;
    average_dimension_scores: Record<string, number>;
    failure_clusters: Record<string, number>;
  };
}
