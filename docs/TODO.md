# List of TODOs

## Candidates

- **`test_convention.md` store example lags F28 (gh#73).** The "Seeding Zustand store" example in `kit/docs/test_convention.md` imports `useAppStore` from `@/shell/appStore`, but F28 in `kit/docs/frontend-rules.md` places the BE/FE shared cache singleton in `infra/cache/` (`useCacheStore.ts`) — `shell/` explicitly rejects app-wide state. The canonical doc teaches a pattern the `reviewer-frontend` F28 grep flags. Fix: align the example to `@/infra/cache/useCacheStore`. The `-svelte` fork (`test_convention-svelte.md`) carries the same pattern but is a separate `svelte-main`-stream decision.

## Experimental
