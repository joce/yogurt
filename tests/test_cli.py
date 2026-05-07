"""Tests for the Yogurt CLI."""

from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

import pytest

from yogurt.cli import main

if TYPE_CHECKING:
    from yogurt.types import ParamValue


class StubClient:
    """Capture CLI calls without touching Yahoo."""

    def __init__(self, body: str = '{"ok":true}') -> None:
        """Initialize the stub client."""

        self.body = body
        self.calls: list[tuple[str, dict[str, ParamValue], bool]] = []
        self.closed = False

    async def get(
        self,
        path: str,
        params: dict[str, ParamValue],
        *,
        use_crumb: bool = True,
    ) -> str:
        """Record the request and return the configured body."""

        self.calls.append((path, params, use_crumb))
        return self.body

    async def aclose(self) -> None:
        """Record that the CLI closed the client."""

        self.closed = True


def test_top_level_help_lists_quote_endpoint(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Top-level help is the command discovery surface."""

    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "commands" in captured.out
    assert "quote" in captured.out
    assert "options" in captured.out
    assert "quote-type" in captured.out
    assert "quote-summary" in captured.out
    assert "price-insights" in captured.out
    assert "calendar-events" in captured.out
    assert "timeseries" in captured.out
    assert "insights" in captured.out
    assert "ratings-top" in captured.out
    assert "chart" in captured.out
    assert "raw" in captured.out
    assert "Retrieve raw" not in captured.out
    assert "Run `yogurt <endpoint> --help`" in captured.out


def test_help_action_text_is_capitalized(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Help and version option descriptions start with capital letters."""

    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Show this help message and exit." in captured.out
    assert "Show the program version and exit." in captured.out
    assert "show this help message and exit" not in captured.out
    assert "show the program's version number and exit" not in captured.out


def test_endpoint_help_action_text_is_capitalized(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Endpoint help uses the same capitalized help action text."""

    with pytest.raises(SystemExit) as exc_info:
        main(["quote", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Show this help message and exit." in captured.out
    assert "show this help message and exit" not in captured.out


def test_version_output_is_capitalized(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Version output starts with Yogurt's capitalized product name."""

    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert captured.out.startswith("Yogurt ")


def test_quote_help_includes_endpoint_params_and_examples(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Endpoint help includes dense result context, params, and examples."""

    with pytest.raises(SystemExit) as exc_info:
        main(["quote", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Prices, trading state, identity, market data" in captured.out
    assert "Calls Yahoo Finance" not in captured.out
    assert "response-model mapping" not in captured.out
    assert "Output:" not in captured.out
    assert "https://query1.finance.yahoo.com/v7/finance/quote" in captured.out
    assert "SYMBOL[,SYMBOL...]" in captured.out
    assert "1 to 10 comma-separated Yahoo symbols" in captured.out
    assert "--fields" in captured.out
    assert "--enable-private-company" in captured.out
    assert "Common --fields values" not in captured.out
    assert "Quote --fields reference" in captured.out
    assert (
        "  ask:                          Lowest price a seller is willing to accept"
        in captured.out
    )
    assert "regularMarketPrice" in captured.out
    assert "customPriceAlertConfidence" in captured.out
    assert "Uses Yahoo crumb/session" not in captured.out
    assert "yogurt quote SMR,OKLO,LEU,VST,CEG" in captured.out


def test_quote_command_passes_params_and_prints_raw_body() -> None:
    """Quote command validates params and writes the raw response body."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "quote",
            "SMR,OKLO",
            "--fields",
            "marketCap,logoUrl,notYetDocumentedByYogurt",
            "--img-heights",
            "50",
            "--img-labels",
            "logoUrl",
            "--img-widths",
            "50",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/v7/finance/quote",
            {
                "symbols": "SMR,OKLO",
                "fields": "marketCap,logoUrl,notYetDocumentedByYogurt",
                "formatted": True,
                "enablePrivateCompany": True,
                "overnightPrice": True,
                "lang": "en-US",
                "region": "US",
                "imgHeights": 50,
                "imgLabels": "logoUrl",
                "imgWidths": 50,
            },
            True,
        )
    ]


def test_quote_command_rejects_more_than_ten_symbols() -> None:
    """Quote command rejects batches larger than Yahoo's observed limit."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "quote",
            "A,B,C,D,E,F,G,H,I,J,K",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert not stdout.getvalue()
    assert "symbols accepts at most 10 comma-separated values; got 11" in (
        stderr.getvalue()
    )
    assert client.closed
    assert not client.calls


def test_options_help_includes_endpoint_params_and_examples(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Options help documents the path symbol and query parameters."""

    with pytest.raises(SystemExit) as exc_info:
        main(["options", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "https://query1.finance.yahoo.com/v7/finance/options/{symbol}" in (
        captured.out
    )
    assert "SYMBOL" in captured.out
    assert "--date" in captured.out
    assert "YYYY-MM-DD" in captured.out
    assert "--formatted" in captured.out
    assert "--straddle" in captured.out
    assert "--lang" in captured.out
    assert "--region" in captured.out
    assert "yogurt options AAPL" in captured.out


def test_options_command_passes_symbol_in_path_and_params() -> None:
    """Options command places the symbol in the path and sends query params."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "options",
            "AAPL",
            "--date",
            "2017-11-17",
            "--formatted",
            "true",
            "--straddle",
            "false",
            "--lang",
            "en-US",
            "--region",
            "US",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/v7/finance/options/AAPL",
            {
                "date": 1510876800,
                "formatted": True,
                "straddle": False,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_options_command_defaults_date_to_negative_one() -> None:
    """Options command defaults date to Yahoo's default-chain sentinel."""

    client = StubClient()
    stdout = StringIO()

    exit_code = main(
        [
            "options",
            "AAPL",
        ],
        stdout=stdout,
        client=client,
    )

    assert exit_code == 0
    assert client.calls == [
        (
            "/v7/finance/options/AAPL",
            {
                "date": -1,
                "formatted": True,
                "straddle": False,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_quote_type_help_includes_endpoint_params_and_examples(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Quote type help documents the symbol and query parameters."""

    with pytest.raises(SystemExit) as exc_info:
        main(["quote-type", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "https://query1.finance.yahoo.com/v1/finance/quoteType" in captured.out
    assert "SYMBOL" in captured.out
    assert "--lang" in captured.out
    assert "--region" in captured.out
    assert "--enable-private-company" in captured.out
    assert "yogurt quote-type AAPL" in captured.out


def test_quote_type_command_passes_symbol_and_common_params() -> None:
    """Quote type command passes the symbol as a query parameter."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "quote-type",
            "AAPL",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/v1/finance/quoteType/",
            {
                "symbol": "AAPL",
                "lang": "en-US",
                "region": "US",
                "enablePrivateCompany": True,
            },
            True,
        )
    ]


def test_quote_summary_help_includes_modules_and_probe_notes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Quote summary help documents modules and live probe caveats."""

    with pytest.raises(SystemExit) as exc_info:
        main(["quote-summary", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}" in (
        captured.out
    )
    assert "--modules" in captured.out
    assert "summaryProfile" in captured.out
    assert "financialData" in captured.out
    assert "recommendationTrend" in captured.out
    assert "equityPerformance" in captured.out
    assert "Yogurt does" in captured.out
    assert "not validate module names" in captured.out
    assert "Common --modules values" not in captured.out
    assert "Quote summary --modules reference" in captured.out
    assert "summaryProfile" in captured.out
    assert "fundProfile" in captured.out
    assert (
        "  fundPerformance:              Fund returns, risk statistics" in captured.out
    )
    assert (
        "  industryTrend:                Industry-level earnings trend" in captured.out
    )
    assert (
        "  topHoldings:                  Fund holdings, sector weights" in captured.out
    )
    assert "esgScores" not in captured.out
    assert "Module availability depends on instrument type" in captured.out


def test_quote_summary_command_passes_symbol_in_path_and_params() -> None:
    """Quote summary command sends modules and common query params."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "quote-summary",
            "AAPL",
            "--modules",
            "summaryProfile,financialData,notYetDocumentedByYogurt",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/v10/finance/quoteSummary/AAPL",
            {
                "modules": "summaryProfile,financialData,notYetDocumentedByYogurt",
                "formatted": True,
                "enablePrivateCompany": True,
                "enableQSPExpandedEarnings": True,
                "overnightPrice": True,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_quote_summary_command_uses_default_modules() -> None:
    """Quote summary command uses the documented default module set."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "quote-summary",
            "AAPL",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/v10/finance/quoteSummary/AAPL",
            {
                "modules": (
                    "summaryProfile,financialData,recommendationTrend,earnings,"
                    "equityPerformance,defaultKeyStatistics"
                ),
                "formatted": True,
                "enablePrivateCompany": True,
                "enableQSPExpandedEarnings": True,
                "overnightPrice": True,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_price_insights_help_includes_params_and_probe_notes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Price insights help documents open params and live probe caveats."""

    with pytest.raises(SystemExit) as exc_info:
        main(["price-insights", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert (
        "https://query1.finance.yahoo.com/ws/company-fundamentals/v1/finance/price-insights"
        in captured.out
    )
    assert "SYMBOL[,SYMBOL...]" in captured.out
    assert "--modules" in captured.out
    assert "--ai-modules" in captured.out
    assert "news_summary" in captured.out
    assert "price_movement" in captured.out
    assert "--check-anomaly" in captured.out
    assert "hasPriceAnomaly-only" in captured.out
    assert "Common --modules values" in captured.out
    assert "modules=ai returned aiAnalysis" in captured.out


def test_price_insights_command_passes_params_and_prints_raw_body() -> None:
    """Price insights command sends Yahoo's open-ended query params."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "price-insights",
            "AAPL,MSFT",
            "--modules",
            "ai",
            "--ai-modules",
            "news_summary,price_movement",
            "--check-anomaly",
            "false",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/ws/company-fundamentals/v1/finance/price-insights",
            {
                "symbols": "AAPL,MSFT",
                "modules": "ai",
                "aiModules": "news_summary,price_movement",
                "checkAnomaly": False,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_price_insights_command_defaults_to_full_response_params() -> None:
    """Price insights omits optional filters by default."""

    client = StubClient()
    stdout = StringIO()

    exit_code = main(
        [
            "price-insights",
            "AAPL",
        ],
        stdout=stdout,
        client=client,
    )

    assert exit_code == 0
    assert client.calls == [
        (
            "/ws/company-fundamentals/v1/finance/price-insights",
            {
                "symbols": "AAPL",
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_calendar_events_help_includes_params_and_probe_notes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Calendar events help documents dates, modules, and observed filters."""

    with pytest.raises(SystemExit) as exc_info:
        main(["calendar-events", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert (
        "https://query1.finance.yahoo.com/ws/screeners/v1/finance/calendar-events"
        in captured.out
    )
    assert "SYMBOL" in captured.out
    assert "--modules" in captured.out
    assert "earnings" in captured.out
    assert "--count-per-day" in captured.out
    assert "--start-date" in captured.out
    assert "--end-date" in captured.out
    assert "milliseconds" in captured.out
    assert "--economic-events-high-importance-only" in captured.out
    assert "--economic-events-region-filter" in captured.out
    assert "Defaults to an empty value when omitted" in captured.out
    assert "--lang" in captured.out
    assert "--region" in captured.out
    assert "yogurt calendar-events AAPL" in captured.out


def test_calendar_events_command_passes_params_and_prints_raw_body() -> None:
    """Calendar events command sends Yahoo's observed query params."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "calendar-events",
            "AAPL",
            "--modules",
            "earnings",
            "--count-per-day",
            "50",
            "--start-date",
            "2026-05-01",
            "--end-date",
            "1777939200000",
            "--economic-events-high-importance-only",
            "false",
            "--economic-events-region-filter",
            "US",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/ws/screeners/v1/finance/calendar-events",
            {
                "modules": "earnings",
                "tickersFilter": "AAPL",
                "countPerDay": 50,
                "startDate": 1777593600000,
                "endDate": 1777939200000,
                "economicEventsHighImportanceOnly": False,
                "economicEventsRegionFilter": "US",
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_calendar_events_command_uses_observed_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Calendar events defaults match the observed Yahoo request shape."""

    client = StubClient()
    stdout = StringIO()
    monkeypatch.setattr("yogurt.cli.time.time", lambda: 1777903200.9)

    exit_code = main(["calendar-events", "AAPL"], stdout=stdout, client=client)

    assert exit_code == 0
    assert client.calls == [
        (
            "/ws/screeners/v1/finance/calendar-events",
            {
                "modules": "earnings",
                "tickersFilter": "AAPL",
                "countPerDay": 100,
                "startDate": 1777644000000,
                "endDate": 1777903200000,
                "economicEventsHighImportanceOnly": True,
                "economicEventsRegionFilter": "",
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_calendar_events_rejects_end_date_before_start_date() -> None:
    """Calendar events rejects reversed millisecond date windows."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        [
            "calendar-events",
            "AAPL",
            "--start-date",
            "1777903200000",
            "--end-date",
            "1777593600000",
        ],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "--end-date must be greater than --start-date" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_calendar_events_rejects_explicit_empty_economic_region_filter() -> None:
    """Only the omitted-option default can send an empty economic region filter."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        [
            "calendar-events",
            "AAPL",
            "--economic-events-region-filter",
            "",
        ],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "economicEventsRegionFilter cannot be empty" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_calendar_events_end_date_without_start_date_is_an_error() -> None:
    """Calendar events requires explicit start-date when end-date is explicit."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        ["calendar-events", "AAPL", "--end-date", "1777593600000"],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "--end-date cannot be provided without --start-date" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_calendar_events_rejects_empty_symbol() -> None:
    """Calendar events requires a non-empty ticker filter."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        ["calendar-events", " "],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "tickersFilter cannot be empty" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_calendar_events_rejects_empty_modules() -> None:
    """Calendar events modules cannot be blank."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        ["calendar-events", "AAPL", "--modules", " "],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "--modules cannot be empty" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_fundamentals_timeseries_help_includes_params_and_type_values(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Fundamentals timeseries help documents dates and observed type values."""

    with pytest.raises(SystemExit) as exc_info:
        main(["timeseries", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert (
        "https://query1.finance.yahoo.com/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}"
        in captured.out
    )
    assert "SYMBOL" in captured.out
    assert "--type" in captured.out
    assert "--period1" in captured.out
    assert "--period2" in captured.out
    assert "recent quote-page window" in captured.out
    assert "current Unix timestamp" in captured.out
    assert "YYYY-MM-DD" in captured.out
    assert "--merge" in captured.out
    assert "--pad-time-series" in captured.out
    assert "Common --type values" not in captured.out
    assert "Timeseries --type reference" in captured.out
    assert (
        "  quarterlyMarketCap:           Quarterly market capitalization"
        in captured.out
    )
    assert (
        "  trailingEnterprisesValueEBITDARatio:\n"
        "                                Trailing enterprise value to EBITDA"
        in captured.out
    )
    assert "  annualTotalRevenue:           Annual total revenue" in captured.out
    assert "  spEarningsReleaseEvents:      S&P earnings release events" in captured.out


@pytest.mark.parametrize(
    "argv",
    [
        ["quote", "AAPL"],
        ["options", "AAPL"],
        ["quote-type", "AAPL"],
        ["quote-summary", "AAPL"],
        ["price-insights", "AAPL"],
        ["calendar-events", "AAPL"],
        ["timeseries", "AAPL"],
        ["insights", "AAPL"],
        ["chart", "AAPL"],
        ["ratings-top", "AAPL"],
    ],
)
def test_endpoint_commands_accept_ticker_only(
    argv: list[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every modeled endpoint can run with only the command and ticker symbol."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()
    monkeypatch.setattr("yogurt.cli.time.time", lambda: 1777903200.9)

    exit_code = main(argv, stdout=stdout, stderr=stderr, client=client)

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert len(client.calls) == 1


def test_fundamentals_timeseries_command_passes_path_and_params() -> None:
    """Fundamentals timeseries command converts dates and sends query params."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "timeseries",
            "AAPL",
            "--period1",
            "2025-11-03",
            "--period2",
            "1777831199",
            "--type",
            "quarterlyMarketCap,trailingMarketCap",
            "--merge",
            "false",
            "--pad-time-series",
            "true",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/ws/fundamentals-timeseries/v1/finance/timeseries/AAPL",
            {
                "type": "quarterlyMarketCap,trailingMarketCap",
                "period1": 1762128000,
                "period2": 1777831199,
                "merge": False,
                "padTimeSeries": True,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_fundamentals_timeseries_command_uses_observed_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fundamentals timeseries command applies observed query defaults."""

    client = StubClient()
    stdout = StringIO()
    monkeypatch.setattr("yogurt.cli.time.time", lambda: 1777903200.9)

    exit_code = main(
        [
            "timeseries",
            "AAPL",
            "--period1",
            "1762192800",
        ],
        stdout=stdout,
        client=client,
    )

    assert exit_code == 0
    assert client.calls == [
        (
            "/ws/fundamentals-timeseries/v1/finance/timeseries/AAPL",
            {
                "type": "spEarningsReleaseEvents,analystRatings,economicEvents",
                "period1": 1762192800,
                "period2": 1777903200,
                "padTimeSeries": True,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_fundamentals_timeseries_command_defaults_period_window(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Timeseries command defaults to a recent quote-page-style window."""

    client = StubClient()
    stdout = StringIO()
    monkeypatch.setattr("yogurt.cli.time.time", lambda: 1777903200.9)

    exit_code = main(["timeseries", "AAPL"], stdout=stdout, client=client)

    assert exit_code == 0
    assert client.calls == [
        (
            "/ws/fundamentals-timeseries/v1/finance/timeseries/AAPL",
            {
                "type": "spEarningsReleaseEvents,analystRatings,economicEvents",
                "period1": 1777644000,
                "period2": 1777903200,
                "padTimeSeries": True,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_period_pair_validation_rejects_period2_before_period1() -> None:
    """Commands with period1/period2 reject reversed windows."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        [
            "timeseries",
            "AAPL",
            "--period1",
            "1777903200",
            "--period2",
            "1777593600",
        ],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "--period2 must be greater than --period1" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_period2_without_period1_is_an_error() -> None:
    """Commands with a period window require period1 when period2 is provided."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        ["timeseries", "AAPL", "--period2", "1777593600"],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "--period2 cannot be provided without --period1" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_insights_help_includes_params_and_probe_notes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Insights help documents params and multi-symbol behavior."""

    with pytest.raises(SystemExit) as exc_info:
        main(["insights", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert (
        "https://query1.finance.yahoo.com/ws/insights/v3/finance/insights"
        in captured.out
    )
    assert "SYMBOL[,SYMBOL...]" in captured.out
    assert "--disable-related-reports" in captured.out
    assert "--formatted" in captured.out
    assert "--get-all-research-reports" in captured.out
    assert "--reports-count" in captured.out
    assert "--ssl" in captured.out
    assert "one finance.result item per requested symbol" in captured.out
    assert "AAPL,MSFT,NVDA" in captured.out


def test_insights_command_passes_params_and_prints_raw_body() -> None:
    """Insights command sends the observed Yahoo query params."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "insights",
            "AAPL,MSFT",
            "--reports-count",
            "8",
            "--disable-related-reports",
            "false",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/ws/insights/v3/finance/insights",
            {
                "symbols": "AAPL,MSFT",
                "disableRelatedReports": False,
                "formatted": True,
                "getAllResearchReports": True,
                "reportsCount": 8,
                "ssl": True,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_insights_command_uses_observed_defaults() -> None:
    """Insights command applies the observed defaults."""

    client = StubClient()
    stdout = StringIO()

    exit_code = main(
        [
            "insights",
            "AAPL",
        ],
        stdout=stdout,
        client=client,
    )

    assert exit_code == 0
    assert client.calls == [
        (
            "/ws/insights/v3/finance/insights",
            {
                "symbols": "AAPL",
                "disableRelatedReports": True,
                "formatted": True,
                "getAllResearchReports": True,
                "reportsCount": 4,
                "ssl": True,
                "lang": "en-US",
                "region": "US",
            },
            True,
        )
    ]


def test_ratings_top_help_includes_params_and_probe_notes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ratings top help documents symbol, filters, and observed score buckets."""

    with pytest.raises(SystemExit) as exc_info:
        main(["ratings-top", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "https://query1.finance.yahoo.com/v2/ratings/top/{symbol}" in captured.out
    assert "SYMBOL" in captured.out
    assert "--exclude-noncurrent" in captured.out
    assert "--lang" in captured.out
    assert "--region" in captured.out
    assert "dir, mm, pt, and fin_score" in captured.out
    assert "yogurt ratings-top AAPL" in captured.out


def test_ratings_top_command_passes_params_and_prints_raw_body() -> None:
    """Ratings top command sends the observed Yahoo query params."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "ratings-top",
            "AAPL",
            "--exclude-noncurrent",
            "false",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/v2/ratings/top/AAPL",
            {
                "exclude_noncurrent": False,
                "lang": "en-US",
                "region": "US",
            },
            False,
        )
    ]


def test_ratings_top_command_uses_observed_defaults() -> None:
    """Ratings top command defaults to Yahoo's current-rating page request."""

    client = StubClient()
    stdout = StringIO()

    exit_code = main(
        [
            "ratings-top",
            "AAPL",
        ],
        stdout=stdout,
        client=client,
    )

    assert exit_code == 0
    assert client.calls == [
        (
            "/v2/ratings/top/AAPL",
            {
                "exclude_noncurrent": True,
                "lang": "en-US",
                "region": "US",
            },
            False,
        )
    ]


def test_chart_help_includes_params_and_examples(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Chart help documents dates, events, and observed chart behavior."""

    with pytest.raises(SystemExit) as exc_info:
        main(["chart", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}" in captured.out
    assert "SYMBOL" in captured.out
    assert "--period1" in captured.out
    assert "--period2" in captured.out
    assert "recent quote-page window" in captured.out
    assert "--interval" in captured.out
    assert "--include-pre-post" in captured.out
    assert "--events" in captured.out
    assert "Supported values: div, split" in captured.out
    assert "earn" in captured.out
    assert "source" not in captured.out
    assert "range" not in captured.out


def test_chart_command_passes_params_and_packs_events() -> None:
    """Chart command sends Yahoo's observed query params."""

    client = StubClient()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [
            "chart",
            "AAPL",
            "--period1",
            "2026-04-30",
            "--period2",
            "1777593600",
            "--interval",
            "1m",
            "--include-pre-post",
            "false",
            "--events",
            "div,earn",
        ],
        stdout=stdout,
        stderr=stderr,
        client=client,
    )

    assert exit_code == 0
    assert stdout.getvalue() == '{"ok":true}\n'
    assert not stderr.getvalue()
    assert client.closed
    assert client.calls == [
        (
            "/v8/finance/chart/AAPL",
            {
                "period1": 1777507200,
                "period2": 1777593600,
                "interval": "1m",
                "includePrePost": False,
                "events": "div|earn",
                "lang": "en-US",
                "region": "US",
            },
            False,
        )
    ]


def test_chart_command_defaults_period2_to_execution_time(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Chart command fills omitted period2 with current Unix time."""

    client = StubClient()
    stdout = StringIO()
    monkeypatch.setattr("yogurt.cli.time.time", lambda: 1777903200.9)

    exit_code = main(
        [
            "chart",
            "AAPL",
            "--period1",
            "1777593600",
        ],
        stdout=stdout,
        client=client,
    )

    assert exit_code == 0
    assert client.calls == [
        (
            "/v8/finance/chart/AAPL",
            {
                "period1": 1777593600,
                "period2": 1777903200,
                "interval": "1m",
                "includePrePost": False,
                "events": "div|split|earn",
                "lang": "en-US",
                "region": "US",
            },
            False,
        )
    ]


def test_chart_command_defaults_period_window_to_quote_page_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Chart command fills omitted period1 and period2 with a recent 3-day window."""

    client = StubClient()
    stdout = StringIO()
    monkeypatch.setattr("yogurt.cli.time.time", lambda: 1777903200.9)

    exit_code = main(
        [
            "chart",
            "AAPL",
        ],
        stdout=stdout,
        client=client,
    )

    assert exit_code == 0
    assert client.calls == [
        (
            "/v8/finance/chart/AAPL",
            {
                "period1": 1777644000,
                "period2": 1777903200,
                "interval": "1m",
                "includePrePost": False,
                "events": "div|split|earn",
                "lang": "en-US",
                "region": "US",
            },
            False,
        )
    ]


def test_chart_command_rejects_period2_without_period1() -> None:
    """Chart requires explicit period1 when period2 is explicitly provided."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        [
            "chart",
            "AAPL",
            "--period2",
            "1777903200",
        ],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "--period2 cannot be provided without --period1" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_chart_command_rejects_now_as_user_period2() -> None:
    """The current-time default is internal, not a user-facing value."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        [
            "chart",
            "AAPL",
            "--period1",
            "1777593600",
            "--period2",
            "now",
        ],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "--period2 expected Unix timestamp" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_chart_command_rejects_unknown_interval() -> None:
    """Chart command rejects intervals outside the observed set."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        [
            "chart",
            "AAPL",
            "--period1",
            "1777593600",
            "--interval",
            "2m",
        ],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "--interval unsupported value '2m'" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_chart_command_rejects_unknown_event() -> None:
    """Chart command validates events because Yahoo silently ignores unknown values."""

    client = StubClient()
    stderr = StringIO()

    exit_code = main(
        [
            "chart",
            "AAPL",
            "--period1",
            "1777593600",
            "--events",
            "div,foo",
        ],
        stderr=stderr,
        client=client,
    )

    assert exit_code == 1
    assert "--events unsupported value 'foo'" in stderr.getvalue()
    assert client.closed
    assert not client.calls


def test_raw_command_passes_path_and_name_value_params() -> None:
    """Raw command calls arbitrary query paths with repeated params."""

    client = StubClient()
    stdout = StringIO()

    exit_code = main(
        [
            "raw",
            "/v7/finance/quote",
            "--param",
            "symbols=AAPL,MSFT",
            "--param",
            "formatted=true",
            "--no-crumb",
        ],
        stdout=stdout,
        client=client,
    )

    assert exit_code == 0
    assert client.calls == [
        (
            "/v7/finance/quote",
            {"symbols": "AAPL,MSFT", "formatted": "true"},
            False,
        )
    ]
