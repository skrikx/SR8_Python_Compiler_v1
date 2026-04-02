<script lang="ts">
  import ArtifactList from '$lib/components/artifacts/ArtifactList.svelte';
  export let data;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Artifacts</div>
  <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">Indexed outputs</h2>
  <p class="mt-3 max-w-3xl text-sm leading-6 text-ink-700">
    These are the real indexed artifacts surfaced by the SR8 backend. If the backend is offline, this view stays empty instead of inventing data.
  </p>
</section>

<div class="mt-5">
  <ArtifactList artifacts={data.artifacts} />
</div>
