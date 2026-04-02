<script lang="ts">
  import '../app.css';
  import { page } from '$app/state';
  import AppShell from '$lib/components/layout/AppShell.svelte';

  export let data;
</script>

<svelte:head>
  <title>SR8</title>
  <meta
    name="description"
    content="SR8 local-first compiler surface with optional provider assist and a thin local product frontend."
  />
</svelte:head>

<AppShell status={data.status} settings={data.settings} active={page.url.pathname}>
  <slot />
</AppShell>
