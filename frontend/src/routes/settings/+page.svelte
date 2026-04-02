<script lang="ts">
  import SettingsForm from '$lib/components/settings/SettingsForm.svelte';
  export let data;
</script>

<section class="glass rounded-[1.75rem] p-5">
  <div class="text-xs uppercase tracking-[0.3em] text-ink-500">Settings</div>
  <h2 class="mt-2 font-display text-3xl font-semibold text-ink-900">Local configuration surface</h2>
  <p class="mt-3 max-w-3xl text-sm leading-6 text-ink-700">
    SR8 settings are backend-owned. The frontend reads them and keeps any local controls honest about what is persisted.
  </p>
</section>

<div class="mt-5">
  <SettingsForm settings={data.settings} />
</div>
