import { env } from '$env/dynamic/private';

import { DEFAULT_API_BASE_URL } from './client';

export function getServerApiBaseUrl(): string {
  return env.SR8_API_BASE_URL || DEFAULT_API_BASE_URL;
}
