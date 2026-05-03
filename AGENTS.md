# AGENTS.md

## Project
Yogurt exposes Yahoo Finance HTTP endpoints as an LLM-friendly CLI that prints the raw JSON Yahoo returns.

## Stack
Python 3.10+, uv, httpx, argparse, pytest, pytest-httpx, ruff, pyright, tox, hatchling.

## Commands
- Install/sync: `uv sync --all-groups`
- Run CLI: `uv run yogurt --help`
- Test single: `uv run pytest path/to/test_file.py`
- Test all: `uv run pytest`
- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Type check: `uv run pyright`
- Spell check: `npm run spell` or `make spell`
- Spell changed files: `npm run spell:changed` or `make spell-changed`
- Full check: `uv run tox`

## Architecture
- `src/yogurt/client.py` -> Yahoo HTTP session, cookies, crumbs, retries, raw response retrieval.
- `src/yogurt/session_cache.py` -> persisted Yahoo cookie/crumb cache for one-shot CLI reuse.
- `src/yogurt/endpoints.py` -> endpoint metadata used to build commands, validation, and help.
- `src/yogurt/params.py` -> CLI parameter coercion and validation helpers.
- `src/yogurt/cli.py` -> argparse command tree and stdout/stderr behavior.
- `tests/` -> pytest tests mirroring `src/yogurt/`.

## Rules
- IMPORTANT: `--help` is the primary product surface; keep it complete, adaptive, and generated from endpoint metadata where practical.
- Do not add `describe`, `endpoints`, `params`, or other discovery commands; discovery belongs under `yogurt --help` and `yogurt <endpoint> --help`.
- Print Yahoo response bodies to stdout exactly as returned; do not model, reshape, pretty-print, or interpret endpoint JSON.
- Keep Yahoo endpoint knowledge in metadata and validation only; do not create response classes.
- Use `uv run python` for Python scripts; never use bare `python` or `python3`.
- Use `greenflame` for screen captures or annotations.
- Never log or print Yahoo cookies, crumbs, or full session-cache contents.
- Keep runtime dependencies narrow; do not add TUI, ORM, web framework, or rich formatting libraries.
- Preserve Calahan's Yahoo cookie/crumb flow unless there is a tested reason to change it.

## Workflow
- Make minimal changes and avoid unrelated refactors.
- When adding an endpoint or parameter, update validation, adaptive help, and tests in the same change.
- Prefer focused unit tests with mocked HTTP; mark live Yahoo tests as integration.
- Before considering code changes done, run `uv run tox`. It is the expected bundled verification for formatting, lint, type check, tests, and spelling.
- For endpoint or parameter changes, also run the app against Yahoo after `tox`:
  - `uv run yogurt <endpoint> --help`
  - `uv run yogurt <endpoint> <minimal required parameters>`
  - `uv run yogurt <endpoint> <parameters with each supported date/time format when dates are involved>`
  - `uv run yogurt <endpoint> <parameters with meaningful modules, types, field lists, booleans, or other values that could affect Yahoo's raw output>`
- When an endpoint has open-ended value lists such as `modules`, `types`, or `fields`, test representative variations and an all-known-values request when practical.
- When a parameter has a default, test both omission and explicit override if the default affects the request sent to Yahoo.
- Ask before making architectural changes that affect the CLI grammar or session-cache behavior.

## Out of scope
- TUI/UX layers from Doubloon.
- Mapping Yahoo JSON into Python domain models.
- Separate documentation/discovery subcommands.
- Secrets, API keys, or checked-in session-cache files.
