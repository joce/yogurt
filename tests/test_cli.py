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
    """Top-level help is the endpoint discovery surface."""

    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "endpoints" in captured.out
    assert "quote" in captured.out
    assert "options" in captured.out
    assert "quote-type" in captured.out
    assert "quote-summary" in captured.out
    assert "price-insights" in captured.out
    assert "insights" in captured.out
    assert "Run `yogurt <endpoint> --help`" in captured.out


def test_quote_help_includes_endpoint_params_and_examples(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Endpoint help includes URL, parameters, crumb policy, and examples."""

    with pytest.raises(SystemExit) as exc_info:
        main(["quote", "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "https://query1.finance.yahoo.com/v7/finance/quote" in captured.out
    assert "SYMBOL[,SYMBOL...]" in captured.out
    assert "1 to 10 comma-separated Yahoo symbols" in captured.out
    assert "--fields" in captured.out
    assert "--enable-private-company" in captured.out
    assert "Common --fields values" in captured.out
    assert "regularMarketPrice" in captured.out
    assert "Uses Yahoo crumb/session" in captured.out
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
    assert "Common --modules values" in captured.out
    assert "summaryProfile" in captured.out
    assert "fundProfile" in captured.out
    assert "esgScores" in captured.out
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
