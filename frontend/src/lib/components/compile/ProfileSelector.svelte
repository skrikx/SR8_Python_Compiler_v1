<script lang="ts">
  export let value = 'generic';
  export let options: string[] = ['generic'];
</script>

<label class="block">
  <div class="mb-2 text-sm font-semibold text-ink-700">Profile selector</div>
  <select
    bind:value
    class="w-full rounded-2xl border border-ink-200 bg-white/90 px-4 py-3 text-sm outline-none transition focus:border-moss-300 focus:ring-2 focus:ring-moss-200/70"
  >
    {#each options as option}
      <option value={option}>{option}</option>
    {/each}
  </select>
</label>
