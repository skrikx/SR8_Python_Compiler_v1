import { writable } from 'svelte/store';

export const workspacePath = writable<string>('.sr8');
export const apiBaseUrl = writable<string>('http://127.0.0.1:8000');
