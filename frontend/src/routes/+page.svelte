<script lang="ts">
  import SystemStatusCard from '$lib/components/status/SystemStatusCard.svelte';
  import WorkspaceStatusCard from '$lib/components/status/WorkspaceStatusCard.svelte';
  import ArtifactList from '$lib/components/artifacts/ArtifactList.svelte';
  import ProviderProbePanel from '$lib/components/providers/ProviderProbePanel.svelte';

  export let data;
</script>

<div class="grid gap-5 xl:grid-cols-2">
  <SystemStatusCard status={data.status} error={data.statusError} />
  <WorkspaceStatusCard
    workspacePath={data.status?.workspace_path ?? '.sr8'}
    apiBaseUrl={data.settings ? 'configured via backend' : 'http://127.0.0.1:8000'}
    available={Boolean(data.status)}
  />
</div>

<div class="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(24rem,0.8fr)]">
  <ArtifactList artifacts={data.artifacts} />
  <ProviderProbePanel probes={data.status?.providers ?? []} />
</div>

