<script lang="ts">
  import ArtifactDetail from '$lib/components/artifacts/ArtifactDetail.svelte';
  export let data;
</script>

{#if data.error}
  <section class="mb-5 rounded-[1.5rem] border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-ink-700">
    {data.error}
  </section>
{/if}

<ArtifactDetail record={data.record} artifact={data.artifact} />
