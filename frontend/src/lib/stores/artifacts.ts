import { writable } from 'svelte/store';

import type { ArtifactRecord } from '$lib/api/types';

export const artifactIndex = writable<ArtifactRecord[]>([]);
export const selectedArtifactId = writable<string>('');
