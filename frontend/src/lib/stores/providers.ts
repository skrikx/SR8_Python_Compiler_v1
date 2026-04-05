import { writable } from 'svelte/store';

import type { ProviderDescriptor, ProviderProbeResult } from '$lib/api/types';

export const providerCatalog = writable<ProviderDescriptor[]>([]);
export const providerProbeState = writable<ProviderProbeResult[]>([]);
export const selectedProvider = writable<string>('rule_based');
