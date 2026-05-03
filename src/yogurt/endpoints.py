"""Yahoo Finance endpoint metadata."""

from __future__ import annotations

from dataclasses import dataclass

from yogurt.params import ParamKind, ParamSpec


@dataclass(frozen=True, slots=True)
class EndpointSpec:
    """Describe a Yahoo Finance endpoint command."""

    name: str
    path: str
    summary: str
    description: str
    params: tuple[ParamSpec, ...]
    examples: tuple[str, ...]
    common_fields: tuple[str, ...] = ()
    common_modules: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    use_crumb: bool = True

    @property
    def yahoo_url(self) -> str:
        """Return the full Yahoo query URL for this endpoint."""

        return f"https://query1.finance.yahoo.com{self.path}"


QUOTE_ENDPOINT = EndpointSpec(
    name="quote",
    path="/v7/finance/quote",
    summary="Retrieve raw quote data for one or more symbols.",
    description=(
        "Calls Yahoo Finance's quote endpoint and writes the response body to "
        "stdout without formatting or response-model mapping."
    ),
    use_crumb=True,
    params=(
        ParamSpec(
            name="symbols",
            cli_name="symbols",
            kind=ParamKind.CSV,
            positional=True,
            required=True,
            metavar="SYMBOL[,SYMBOL...]",
            min_items=1,
            max_items=10,
            help=(
                "1 to 10 comma-separated Yahoo symbols, such as AAPL,MSFT or SHOP.TO."
            ),
        ),
        ParamSpec(
            name="fields",
            cli_name="fields",
            kind=ParamKind.CSV,
            metavar="FIELD[,FIELD...]",
            help=(
                "Optional comma-separated Yahoo quote fields to request. "
                "Yogurt does not validate field names."
            ),
        ),
        ParamSpec(
            name="formatted",
            cli_name="formatted",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request Yahoo formatted values.",
        ),
        ParamSpec(
            name="enablePrivateCompany",
            cli_name="enable-private-company",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Include private company quote matches when Yahoo supports them.",
        ),
        ParamSpec(
            name="overnightPrice",
            cli_name="overnight-price",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request overnight price fields when available.",
        ),
        ParamSpec(
            name="lang",
            cli_name="lang",
            kind=ParamKind.STRING,
            default="en-US",
            metavar="LANG",
            help="Yahoo response language.",
        ),
        ParamSpec(
            name="region",
            cli_name="region",
            kind=ParamKind.STRING,
            default="US",
            metavar="REGION",
            help="Yahoo response region.",
        ),
        ParamSpec(
            name="imgHeights",
            cli_name="img-heights",
            kind=ParamKind.INTEGER,
            metavar="PIXELS",
            help="Logo/image height requested from Yahoo.",
        ),
        ParamSpec(
            name="imgLabels",
            cli_name="img-labels",
            kind=ParamKind.CSV,
            metavar="LABEL[,LABEL...]",
            help="Image labels to request, such as logoUrl.",
        ),
        ParamSpec(
            name="imgWidths",
            cli_name="img-widths",
            kind=ParamKind.INTEGER,
            metavar="PIXELS",
            help="Logo/image width requested from Yahoo.",
        ),
    ),
    examples=(
        "yogurt quote SMR,OKLO,LEU,VST,CEG",
        (
            "yogurt quote SMR,SERV,SYM,GEV,LASE,RR "
            "--fields marketCap,morningstarIndustry,logoUrl,longName,"
            "regularMarketPrice,regularMarketChange,regularMarketChangePercent,"
            "shortName,regularMarketTime,regularMarketVolume "
            "--img-heights 50 --img-labels logoUrl --img-widths 50"
        ),
    ),
    common_fields=(
        "symbol",
        "shortName",
        "longName",
        "displayName",
        "quoteType",
        "marketCap",
        "morningstarIndustry",
        "logoUrl",
        "regularMarketPrice",
        "regularMarketChange",
        "regularMarketChangePercent",
        "regularMarketTime",
        "regularMarketVolume",
        "marketState",
        "fiftyTwoWeekLow",
        "fiftyTwoWeekHigh",
        "averageAnalystRating",
    ),
)

OPTIONS_ENDPOINT = EndpointSpec(
    name="options",
    path="/v7/finance/options/{symbol}",
    summary="Retrieve raw option chain data for a single symbol.",
    description=(
        "Calls Yahoo Finance's options endpoint for one symbol and writes the "
        "response body to stdout without formatting or response-model mapping."
    ),
    use_crumb=True,
    params=(
        ParamSpec(
            name="symbol",
            cli_name="symbol",
            kind=ParamKind.STRING,
            positional=True,
            path_param=True,
            required=True,
            metavar="SYMBOL",
            help="A single Yahoo symbol, such as AAPL or SHOP.TO.",
        ),
        ParamSpec(
            name="date",
            cli_name="date",
            kind=ParamKind.DATETIME,
            default=-1,
            metavar="DATE",
            help=(
                "Option expiration date as a Unix timestamp, YYYY-MM-DD date, "
                "or ISO datetime. Date-only values are converted at UTC midnight. "
                "Yahoo uses -1 for the default chain."
            ),
        ),
        ParamSpec(
            name="formatted",
            cli_name="formatted",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request Yahoo formatted values.",
        ),
        ParamSpec(
            name="straddle",
            cli_name="straddle",
            kind=ParamKind.BOOLEAN,
            default=False,
            metavar="BOOL",
            help="Request Yahoo straddle data when available.",
        ),
        ParamSpec(
            name="lang",
            cli_name="lang",
            kind=ParamKind.STRING,
            default="en-US",
            metavar="LANG",
            help="Yahoo response language.",
        ),
        ParamSpec(
            name="region",
            cli_name="region",
            kind=ParamKind.STRING,
            default="US",
            metavar="REGION",
            help="Yahoo response region.",
        ),
    ),
    examples=(
        "yogurt options AAPL",
        "yogurt options AAPL --date 2017-11-17",
        "yogurt options AAPL --date 1510876800 --formatted true --straddle false",
    ),
)

QUOTE_TYPE_ENDPOINT = EndpointSpec(
    name="quote-type",
    path="/v1/finance/quoteType/",
    summary="Retrieve raw quote type data for a single symbol.",
    description=(
        "Calls Yahoo Finance's quoteType endpoint for one symbol and writes the "
        "response body to stdout without formatting or response-model mapping."
    ),
    use_crumb=True,
    params=(
        ParamSpec(
            name="symbol",
            cli_name="symbol",
            kind=ParamKind.STRING,
            positional=True,
            required=True,
            metavar="SYMBOL",
            help="A single Yahoo symbol, such as AAPL or SHOP.TO.",
        ),
        ParamSpec(
            name="lang",
            cli_name="lang",
            kind=ParamKind.STRING,
            default="en-US",
            metavar="LANG",
            help="Yahoo response language.",
        ),
        ParamSpec(
            name="region",
            cli_name="region",
            kind=ParamKind.STRING,
            default="US",
            metavar="REGION",
            help="Yahoo response region.",
        ),
        ParamSpec(
            name="enablePrivateCompany",
            cli_name="enable-private-company",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Include private company data when Yahoo supports it.",
        ),
    ),
    examples=(
        "yogurt quote-type AAPL",
        "yogurt quote-type AAPL --enable-private-company true",
    ),
)

QUOTE_SUMMARY_ENDPOINT = EndpointSpec(
    name="quote-summary",
    path="/v10/finance/quoteSummary/{symbol}",
    summary="Retrieve raw quote summary modules for a single symbol.",
    description=(
        "Calls Yahoo Finance's quoteSummary endpoint for one symbol and writes "
        "the response body to stdout without formatting or response-model mapping."
    ),
    use_crumb=True,
    params=(
        ParamSpec(
            name="symbol",
            cli_name="symbol",
            kind=ParamKind.STRING,
            positional=True,
            path_param=True,
            required=True,
            metavar="SYMBOL",
            help="A single Yahoo symbol, such as AAPL or SHOP.TO.",
        ),
        ParamSpec(
            name="modules",
            cli_name="modules",
            kind=ParamKind.CSV,
            default=(
                "summaryProfile,financialData,recommendationTrend,earnings,"
                "equityPerformance,defaultKeyStatistics"
            ),
            metavar="MODULE[,MODULE...]",
            help=(
                "Comma-separated Yahoo quoteSummary modules to request. "
                "Yogurt does not validate module names."
            ),
        ),
        ParamSpec(
            name="formatted",
            cli_name="formatted",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request Yahoo formatted values.",
        ),
        ParamSpec(
            name="enablePrivateCompany",
            cli_name="enable-private-company",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Include private company data when Yahoo supports it.",
        ),
        ParamSpec(
            name="enableQSPExpandedEarnings",
            cli_name="enable-qsp-expanded-earnings",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request Yahoo expanded quote summary earnings fields.",
        ),
        ParamSpec(
            name="overnightPrice",
            cli_name="overnight-price",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request overnight price fields when available.",
        ),
        ParamSpec(
            name="lang",
            cli_name="lang",
            kind=ParamKind.STRING,
            default="en-US",
            metavar="LANG",
            help="Yahoo response language.",
        ),
        ParamSpec(
            name="region",
            cli_name="region",
            kind=ParamKind.STRING,
            default="US",
            metavar="REGION",
            help="Yahoo response region.",
        ),
    ),
    examples=(
        "yogurt quote-summary AAPL",
        "yogurt quote-summary AAPL --modules price,quoteType,summaryDetail",
    ),
    common_modules=(
        "summaryDetail",
        "assetProfile",
        "fundProfile",
        "financialData",
        "defaultKeyStatistics",
        "calendarEvents",
        "incomeStatementHistory",
        "incomeStatementHistoryQuarterly",
        "cashflowStatementHistory",
        "cashflowStatementHistoryQuarterly",
        "balanceSheetHistory",
        "balanceSheetHistoryQuarterly",
        "earnings",
        "earningsHistory",
        "insiderHolders",
        "insiderTransactions",
        "secFilings",
        "indexTrend",
        "sectorTrend",
        "earningsTrend",
        "netSharePurchaseActivity",
        "upgradeDowngradeHistory",
        "institutionOwnership",
        "recommendationTrend",
        "fundOwnership",
        "majorDirectHolders",
        "majorHoldersBreakdown",
        "price",
        "quoteType",
        "summaryProfile",
        "equityPerformance",
    ),
    notes=(
        "Module availability depends on instrument type.",
        "Live AAPL probe populated all listed common modules except fundProfile.",
        "Live VT probe populated fundProfile.",
        "Live AAPL and MSFT probes returned HTTP 404 for esgScores.",
    ),
)

PRICE_INSIGHTS_ENDPOINT = EndpointSpec(
    name="price-insights",
    path="/ws/company-fundamentals/v1/finance/price-insights",
    summary="Retrieve raw generated price insight data for one or more symbols.",
    description=(
        "Calls Yahoo Finance's price-insights endpoint and writes the response "
        "body to stdout without formatting or response-model mapping."
    ),
    use_crumb=True,
    params=(
        ParamSpec(
            name="symbols",
            cli_name="symbols",
            kind=ParamKind.CSV,
            positional=True,
            required=True,
            metavar="SYMBOL[,SYMBOL...]",
            min_items=1,
            help=(
                "One or more comma-separated Yahoo symbols, such as AAPL or AAPL,MSFT."
            ),
        ),
        ParamSpec(
            name="modules",
            cli_name="modules",
            kind=ParamKind.CSV,
            metavar="MODULE[,MODULE...]",
            help=(
                "Optional comma-separated Yahoo price-insights modules to request. "
                "Observed useful value: ai. Yogurt does not validate module names."
            ),
        ),
        ParamSpec(
            name="aiModules",
            cli_name="ai-modules",
            kind=ParamKind.CSV,
            metavar="AI_MODULE[,AI_MODULE...]",
            help=(
                "Optional comma-separated Yahoo AI submodules to request. "
                "Observed values: news_summary,price_movement. Yogurt does not "
                "validate names."
            ),
        ),
        ParamSpec(
            name="checkAnomaly",
            cli_name="check-anomaly",
            kind=ParamKind.BOOLEAN,
            metavar="BOOL",
            help=(
                "Ask Yahoo to check only for a price anomaly. Observed true value "
                "returns a tiny hasPriceAnomaly-only response."
            ),
        ),
        ParamSpec(
            name="lang",
            cli_name="lang",
            kind=ParamKind.STRING,
            default="en-US",
            metavar="LANG",
            help="Yahoo response language.",
        ),
        ParamSpec(
            name="region",
            cli_name="region",
            kind=ParamKind.STRING,
            default="US",
            metavar="REGION",
            help="Yahoo response region.",
        ),
    ),
    examples=(
        "yogurt price-insights AAPL",
        "yogurt price-insights AAPL,MSFT --modules ai",
        ("yogurt price-insights AAPL --ai-modules news_summary,price_movement"),
    ),
    common_modules=("ai",),
    notes=(
        (
            "Omitting modules returned news, aiAnalysis, analystRating, and "
            "anomaly data in live AAPL probes."
        ),
        (
            "modules=ai returned aiAnalysis and hasPriceAnomaly without the "
            "surrounding news/rating sections."
        ),
        (
            "aiModules=news_summary,price_movement did not change the live "
            "AAPL response when modules was omitted."
        ),
        "checkAnomaly=false behaved like omission in live AAPL probes.",
        "checkAnomaly=true returned only hasPriceAnomaly in live AAPL probes.",
    ),
)

ENDPOINTS: tuple[EndpointSpec, ...] = (
    QUOTE_ENDPOINT,
    OPTIONS_ENDPOINT,
    QUOTE_TYPE_ENDPOINT,
    QUOTE_SUMMARY_ENDPOINT,
    PRICE_INSIGHTS_ENDPOINT,
)
ENDPOINTS_BY_NAME: dict[str, EndpointSpec] = {
    endpoint.name: endpoint for endpoint in ENDPOINTS
}
