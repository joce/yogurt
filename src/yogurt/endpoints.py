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
    common_types: tuple[str, ...] = ()
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

FUNDAMENTALS_TIMESERIES_ENDPOINT = EndpointSpec(
    name="timeseries",
    path="/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}",
    summary="Retrieve raw fundamentals timeseries data for a single symbol.",
    description=(
        "Calls Yahoo Finance's fundamentals timeseries endpoint for one symbol "
        "and writes the response body to stdout without formatting or "
        "response-model mapping."
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
            name="type",
            cli_name="type",
            kind=ParamKind.CSV,
            default="spEarningsReleaseEvents,analystRatings,economicEvents",
            metavar="TYPE[,TYPE...]",
            min_items=1,
            help=(
                "One or more comma-separated Yahoo fundamentals timeseries "
                "types to request. Yogurt does not validate type names."
            ),
        ),
        ParamSpec(
            name="period1",
            cli_name="period1",
            kind=ParamKind.DATETIME,
            required=True,
            metavar="DATE",
            help=(
                "Start date as a Unix timestamp, YYYY-MM-DD date, or ISO "
                "datetime. Date-only values are converted at UTC midnight."
            ),
        ),
        ParamSpec(
            name="period2",
            cli_name="period2",
            kind=ParamKind.DATETIME,
            default="today",
            metavar="DATE",
            help=(
                "End date as a Unix timestamp, YYYY-MM-DD date, or ISO "
                "datetime. Defaults to today's date. Date-only values are "
                "converted at UTC midnight."
            ),
        ),
        ParamSpec(
            name="merge",
            cli_name="merge",
            kind=ParamKind.BOOLEAN,
            default=False,
            metavar="BOOL",
            help="Ask Yahoo to merge timeseries results when supported.",
        ),
        ParamSpec(
            name="padTimeSeries",
            cli_name="pad-time-series",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Ask Yahoo to pad missing timeseries values when supported.",
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
        (
            "yogurt timeseries AAPL --period1 2025-11-03 "
            "--period2 2026-05-03 --type quarterlyMarketCap,trailingMarketCap"
        ),
        (
            "yogurt timeseries AAPL --period1 1762192800 "
            "--period2 1777831199 --type quarterlyPeRatio,trailingPeRatio "
            "--merge false --pad-time-series true"
        ),
    ),
    common_types=(
        "spEarningsReleaseEvents",
        "analystRatings",
        "economicEvents",
        "quarterlyMarketCap",
        "trailingMarketCap",
        "quarterlyEnterpriseValue",
        "trailingEnterpriseValue",
        "quarterlyPeRatio",
        "trailingPeRatio",
        "quarterlyForwardPeRatio",
        "trailingForwardPeRatio",
        "quarterlyPegRatio",
        "trailingPegRatio",
        "quarterlyPsRatio",
        "trailingPsRatio",
        "quarterlyPbRatio",
        "trailingPbRatio",
        "quarterlyEnterprisesValueRevenueRatio",
        "trailingEnterprisesValueRevenueRatio",
        "quarterlyEnterprisesValueEBITDARatio",
        "trailingEnterprisesValueEBITDARatio",
    ),
    notes=(
        "The --type parameter is open-ended; availability depends on symbol.",
        (
            "period1 and period2 accept Unix timestamps, YYYY-MM-DD dates, "
            "or ISO datetimes."
        ),
    ),
)

INSIGHTS_ENDPOINT = EndpointSpec(
    name="insights",
    path="/ws/insights/v3/finance/insights",
    summary="Retrieve raw insight data for one or more symbols.",
    description=(
        "Calls Yahoo Finance's insights endpoint and writes the response body "
        "to stdout without formatting or response-model mapping."
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
            name="disableRelatedReports",
            cli_name="disable-related-reports",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Ask Yahoo not to include related research reports.",
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
            name="getAllResearchReports",
            cli_name="get-all-research-reports",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request all available research reports when Yahoo supports them.",
        ),
        ParamSpec(
            name="reportsCount",
            cli_name="reports-count",
            kind=ParamKind.INTEGER,
            default=4,
            metavar="COUNT",
            help="Number of research reports to request.",
        ),
        ParamSpec(
            name="ssl",
            cli_name="ssl",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request SSL URLs in Yahoo response fields when available.",
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
        "yogurt insights AAPL",
        "yogurt insights AAPL,MSFT",
        "yogurt insights AAPL --reports-count 4",
    ),
    notes=(
        "Live probes returned one finance.result item per requested symbol.",
        "AAPL,MSFT,NVDA returned three result objects in live probing.",
    ),
)

RATINGS_TOP_ENDPOINT = EndpointSpec(
    name="ratings-top",
    path="/v2/ratings/top/{symbol}",
    summary="Retrieve raw top analyst rating scores for a single symbol.",
    description=(
        "Calls Yahoo Finance's top ratings endpoint for one symbol and writes "
        "the response body to stdout without formatting or response-model mapping."
    ),
    use_crumb=False,
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
            name="exclude_noncurrent",
            cli_name="exclude-noncurrent",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help=(
                "Exclude non-current analyst records from Yahoo's top scored "
                "rating buckets."
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
        "yogurt ratings-top AAPL",
        "yogurt ratings-top AAPL --exclude-noncurrent false",
    ),
    notes=(
        (
            "Observed Yahoo quote pages request exclude_noncurrent=true and "
            "return dir, mm, pt, and fin_score top analyst buckets."
        ),
        (
            "exclude_noncurrent=false can return older scored analyst records "
            "with null current rating and price-target fields."
        ),
    ),
)

ENDPOINTS: tuple[EndpointSpec, ...] = (
    QUOTE_ENDPOINT,
    OPTIONS_ENDPOINT,
    QUOTE_TYPE_ENDPOINT,
    QUOTE_SUMMARY_ENDPOINT,
    PRICE_INSIGHTS_ENDPOINT,
    FUNDAMENTALS_TIMESERIES_ENDPOINT,
    INSIGHTS_ENDPOINT,
    RATINGS_TOP_ENDPOINT,
)
ENDPOINTS_BY_NAME: dict[str, EndpointSpec] = {
    endpoint.name: endpoint for endpoint in ENDPOINTS
}
