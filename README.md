# Yogurt

[![CI](https://github.com/joce/yogurt/actions/workflows/ci.yml/badge.svg)](https://github.com/joce/yogurt/actions/workflows/ci.yml)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GitHub License](https://img.shields.io/github/license/joce/yogurt)](https://github.com/joce/yogurt/blob/main/LICENSE)

Yahoo!-Originated Graphs, Updates, Returns & Tickers.

Yogurt brings Yahoo Finance's HTTP endpoints to the command line. It is built
for scripts, agents, and quick terminal work that needs the JSON returned by
Yahoo's finance endpoints.

The project stays deliberately close to the source. It does not reshape Yahoo
responses, define finance domain models, or add a discovery API beyond CLI
help.

## Features

- Raw Yahoo Finance JSON on stdout, with no pretty-printing or interpretation.
- Endpoint-specific commands for common Yahoo Finance data.
- Generated help that includes examples, parameters, field references, modules,
  or types when Yogurt knows them.
- Reusable Yahoo session cache for faster one-shot CLI calls.
- A `raw` command for Yahoo query paths that do not have dedicated metadata yet.

## Install From Source

Yogurt is currently intended to run from a local checkout. It is a Python 3.10+
project managed with [uv](https://docs.astral.sh/uv/).

```powershell
uv sync --all-groups
```

Run the CLI from the repository:

```powershell
uv run yogurt --help
```

Or install it as a package from a local checkout:

```powershell
uv tool install .
yogurt --help
```

## Quick Start

Fetch quotes for a few symbols:

```powershell
uv run yogurt quote AAPL,MSFT,NVDA
```

Request specific quote fields:

```powershell
uv run yogurt quote AAPL,MSFT --fields symbol,longName,regularMarketPrice,regularMarketChangePercent
```

See [QUOTE_FIELDS.md](QUOTE_FIELDS.md) for the full quote field reference and
best-effort meanings.

Fetch selected quote summary modules:

```powershell
uv run yogurt quote-summary AAPL --modules price,quoteType,summaryDetail
```

Fetch chart data for a recent window:

```powershell
uv run yogurt chart AAPL
```

Fetch an option chain using Yahoo's default expiration:

```powershell
uv run yogurt options AAPL
```

Pass through a Yahoo query path directly:

```powershell
uv run yogurt raw /v7/finance/quote --param symbols=AAPL,MSFT --param formatted=true
```

## Commands

Use root help to see the command list:

```powershell
uv run yogurt --help
```

Current commands include:

| Command | Yahoo data |
| --- | --- |
| `quote` | Quote data for one or more symbols. |
| `options` | Option chain data for a single symbol. |
| `quote-type` | Quote type data for a single symbol. |
| `quote-summary` | Quote summary modules for a single symbol. |
| `price-insights` | Generated price insight data for one or more symbols. |
| `timeseries` | Fundamentals timeseries data for a single symbol. |
| `insights` | Insight data for one or more symbols. |
| `chart` | Chart price data for a single symbol. |
| `ratings-top` | Top analyst rating scores for a single symbol. |
| `raw` | Custom Yahoo query path for data Yogurt does not model yet. |

Each endpoint has its own adaptive help:

```powershell
uv run yogurt quote --help
uv run yogurt quote-summary --help
uv run yogurt timeseries --help
```

Endpoint help is the primary documentation surface. It shows Yahoo's target
endpoint, accepted parameters, defaults, examples, and common open-ended values
where available.

### Chart

The `chart` command calls Yahoo's `/v8/finance/chart/{symbol}` endpoint without
requesting a crumb:

```powershell
uv run yogurt chart AAPL
```

When period arguments are omitted, Yogurt uses a recent quote-page-shaped
window: `period1` defaults to three days before execution time, `period2`
defaults to execution time, `--interval` defaults to `1m`, and `--events`
defaults to `div,split,earn`. User-provided events are comma-separated; Yogurt
packs them for Yahoo internally. Extended-hours data is opt-in with
`--include-pre-post true`.

### Timeseries

The `timeseries` command can also run with only a ticker:

```powershell
uv run yogurt timeseries AAPL
```

Its default type list matches the Yahoo quote/analysis page request for
earnings-release, analyst-rating, and economic-event timeseries data. When
period arguments are omitted, Yogurt uses a recent quote-page-style window:
`period1` defaults to three days before execution time and `period2` defaults
to execution time.

## Dates and Booleans

Date and datetime parameters accept:

- Unix timestamps, such as `1510876800`.
- Date-only values, such as `2017-11-17`.
- ISO datetime values.

Date-only values are converted at UTC midnight before they are sent to Yahoo.
For endpoints with `period1` and `period2`, documented defaults let ticker-only
requests run, `period2` defaults to the current Unix timestamp when omitted, and
Yogurt rejects windows where `period2` is not greater than `period1`. Supplying
`period2` without `period1` is also rejected.

Boolean parameters accept common true and false forms such as `true`, `false`,
`1`, `0`, `yes`, and `no`.

## Session Cache

Most Yahoo endpoints require a cookie and crumb. Yogurt establishes that session
state automatically and caches it for reuse across CLI calls.

Useful global options:

```powershell
uv run yogurt --refresh-session quote AAPL
uv run yogurt --no-session-cache quote AAPL
uv run yogurt --session-cache C:\tmp\yogurt-session.json quote AAPL
```

Yogurt never prints cookies, crumbs, or full session-cache contents.

## Output Contract

Yogurt writes the Yahoo response body to stdout exactly as returned. This makes
it easy to pipe into tools that expect JSON:

```powershell
uv run yogurt quote AAPL | jq .
```

Diagnostics and errors are written to stderr.

## Development

Install development dependencies:

```powershell
uv sync --all-groups
```

Run the test suite:

```powershell
uv run pytest
```

Run checks locally:

```powershell
uv run black --check .
uv run ruff format --check --diff .
uv run ruff check .
uv run pyright
uv run pytest -n auto
```

Run the full project check, including Python checks and spelling:

```powershell
uv run tox
```

When adding or changing command metadata, update validation, adaptive help, and
tests together. Then verify the relevant command against Yahoo with its help,
minimal required parameters, and representative optional parameters.

## License

Yogurt is released under the MIT License. See [LICENSE](LICENSE).
