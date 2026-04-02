<script lang="ts">
  import Sidebar from './Sidebar.svelte';
  import Topbar from './Topbar.svelte';
  import type { SettingsSnapshot, StatusSnapshot } from '$lib/api/types';

  export let status: StatusSnapshot | null = null;
  export let settings: SettingsSnapshot | null = null;
  export let active = '/';
</script>

<div class="mx-auto grid min-h-screen max-w-[1600px] gap-6 p-4 lg:grid-cols-[19rem_minmax(0,1fr)] lg:p-6">
  <aside class="glass-strong rounded-[2rem]">
    <Sidebar {active} />
  </aside>
  <main class="flex min-w-0 flex-col gap-6">
    <Topbar {status} {settings} />
    <div class="min-w-0 flex-1">
      <slot />
    </div>
  </main>
</div>
