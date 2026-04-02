import { writable } from 'svelte/store';

export interface SessionState {
  profile: string;
  provider: string;
  assistantEnabled: boolean;
}

export const session = writable<SessionState>({
  profile: 'generic',
  provider: 'rule_based',
  assistantEnabled: false
});
