# List of TODOs

## Candidates

- **`visual-proof-capture.mjs` ships tab-indented, fails downstream biome (gh#77).** The kit's `just format`/`lint-scripts` run biome with no project config, so biome's default `indentStyle: tab` formats the shipped `.mjs` with tabs. Downstream projects pin `indentStyle: space`, so the synced file fails their biome on every sync. Fix: add `--indent-style=space` to the kit's biome CLI invocations (no project config — preserves the "CLI flags only" design) and reformat the `.mjs`.

## Experimental
