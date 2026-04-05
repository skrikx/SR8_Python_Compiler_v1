# Frontend

SR8 now includes a local SvelteKit frontend in `frontend/`.

## Goals

- thin UI over real SR8 API state
- SSR-first local web app
- visible trust surfaces for confidence, validation, lineage, and receipts
- usable with zero provider configuration

## Routes

- `/` dashboard
- `/compile`
- `/artifacts`
- `/artifacts/[id]`
- `/transforms`
- `/diff`
- `/lint`
- `/receipts`
- `/benchmarks`
- `/providers`
- `/settings`

## Local Run

Start the backend API separately, then run the frontend:

```bash
cd frontend
npm install
npm run check
npm run build
npm run dev
```

If your API is not on the default local address, set:

```bash
SR8_API_BASE_URL=http://127.0.0.1:8000
```

## Contract

- The frontend fetches backend data through `src/lib/api/client.ts`.
- Server load functions use the backend directly and do not duplicate compiler logic.
- Empty or unavailable backend states remain visible instead of being replaced with fake data.
