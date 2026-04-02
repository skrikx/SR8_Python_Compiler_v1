<script lang="ts">
  import type { ArtifactRecord } from '$lib/api/types';

  export let artifact: ArtifactRecord;
</script>

<a
  href={`/artifacts/${artifact.artifact_id}`}
  class="block rounded-[1.5rem] border border-ink-200 bg-white/85 p-4 transition hover:-translate-y-0.5 hover:shadow-glow"
>
  <div class="flex items-start justify-between gap-4">
    <div>
      <div class="text-xs uppercase tracking-[0.25em] text-ink-500">{artifact.artifact_kind}</div>
      <div class="mt-1 font-semibold text-ink-900">{artifact.artifact_id}</div>
    </div>
    <span class="rounded-full border border-moss-200 bg-moss-50 px-3 py-1 text-xs text-moss-800">
      {artifact.readiness_status}
    </span>
  </div>
  <div class="mt-3 text-sm text-ink-700">Profile: {artifact.profile}</div>
  <div class="mt-1 text-sm text-ink-700">Target: {artifact.target_class}</div>
</a>
