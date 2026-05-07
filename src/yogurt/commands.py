"""Yahoo Finance command metadata."""

from __future__ import annotations

from dataclasses import dataclass

from yogurt.params import ParamKind, ParamSpec


@dataclass(frozen=True, slots=True)
class FieldReference:
    """Describe a known open-ended Yahoo parameter value."""

    name: str
    description: str


@dataclass(frozen=True, slots=True)
class CommandSpec:
    """Describe one Yogurt command backed by a Yahoo Finance endpoint."""

    name: str
    path: str
    summary: str
    description: str
    params: tuple[ParamSpec, ...]
    examples: tuple[str, ...]
    field_reference: tuple[FieldReference, ...] = ()
    field_reference_title: str = "Quote --fields reference"
    common_modules: tuple[str, ...] = ()
    common_types: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    use_crumb: bool = True

    @property
    def yahoo_url(self) -> str:
        """Return the full Yahoo query URL for this endpoint."""

        return f"https://query1.finance.yahoo.com{self.path}"


def _prefixed_field_references(
    prefixes: tuple[FieldReference, ...],
    metrics: tuple[FieldReference, ...],
) -> tuple[FieldReference, ...]:
    """Return Yahoo timeseries type references with generated prefixes."""

    return tuple(
        FieldReference(
            f"{prefix.name}{metric.name}",
            f"{prefix.description} {metric.description}",
        )
        for prefix in prefixes
        for metric in metrics
    )


_TIMESERIES_EVENTS: tuple[FieldReference, ...] = (
    FieldReference("spEarningsReleaseEvents", "S&P earnings release events"),
    FieldReference("analystRatings", "analyst ratings"),
    FieldReference("economicEvents", "economic events"),
)

_TIMESERIES_ANNUAL_PREFIXES: tuple[FieldReference, ...] = (
    FieldReference("annual", "Annual"),
)

_TIMESERIES_QUARTERLY_TRAILING_PREFIXES: tuple[FieldReference, ...] = (
    FieldReference("quarterly", "Quarterly"),
    FieldReference("trailing", "Trailing"),
)

_TIMESERIES_VALUATION_METRICS: tuple[FieldReference, ...] = (
    FieldReference("MarketCap", "market capitalization"),
    FieldReference("EnterpriseValue", "enterprise value"),
    FieldReference("PeRatio", "P/E ratio"),
    FieldReference("ForwardPeRatio", "forward P/E ratio"),
    FieldReference("PegRatio", "PEG ratio"),
    FieldReference("PsRatio", "price to sales ratio"),
    FieldReference("PbRatio", "price to book ratio"),
    FieldReference("EnterprisesValueRevenueRatio", "enterprise value to revenue"),
    FieldReference("EnterprisesValueEBITDARatio", "enterprise value to EBITDA"),
)

_TIMESERIES_ANNUAL_METRICS: tuple[FieldReference, ...] = (
    FieldReference("InterestExpense", "interest expense"),
    FieldReference("OtherIncomeExpense", "other income or expense"),
    FieldReference("OperatingCashFlow", "operating cash flow"),
    FieldReference("PurchaseOfInvestment", "investment purchases"),
    FieldReference("EndCashPosition", "ending cash position"),
    FieldReference("BeginningCashPosition", "beginning cash position"),
    FieldReference("NetOtherFinancingCharges", "net other financing charges"),
    FieldReference("RepurchaseOfCapitalStock", "capital stock repurchases"),
    FieldReference("RepaymentOfDebt", "debt repayments"),
    FieldReference("SaleOfInvestment", "investment sales"),
    FieldReference("PurchaseOfBusiness", "business purchases"),
    FieldReference("OtherNonCashItems", "other non-cash items"),
    FieldReference("FreeCashFlow", "free cash flow"),
    FieldReference("AccountsPayable", "accounts payable"),
    FieldReference("StockBasedCompensation", "stock-based compensation"),
    FieldReference("DeferredIncomeTax", "deferred income tax"),
    FieldReference("ChangeInWorkingCapital", "change in working capital"),
    FieldReference("CostOfRevenue", "cost of revenue"),
    FieldReference("EBITDA", "EBITDA"),
    FieldReference("NormalizedEBITDA", "normalized EBITDA"),
    FieldReference("OperatingIncome", "operating income"),
    FieldReference("StockholdersEquity", "stockholders' equity"),
    FieldReference("CurrentLiabilities", "current liabilities"),
    FieldReference(
        "TotalLiabilitiesNetMinorityInterest",
        "total liabilities net minority interest",
    ),
    FieldReference("CurrentAssets", "current assets"),
    FieldReference("TotalAssets", "total assets"),
    FieldReference("ChangesInAccountReceivables", "changes in account receivables"),
    FieldReference("CapitalExpenditure", "capital expenditure"),
    FieldReference("NetOtherInvestingChanges", "net other investing changes"),
    FieldReference(
        "CashFlowFromContinuingFinancingActivities",
        "cash flow from continuing financing activities",
    ),
    FieldReference(
        "ChangeInCashSupplementalAsReported",
        "supplemental change in cash as reported",
    ),
    FieldReference("DepreciationAndAmortization", "depreciation and amortization"),
    FieldReference("ChangeInInventory", "change in inventory"),
    FieldReference("InvestingCashFlow", "investing cash flow"),
    FieldReference("CommonStockIssuance", "common stock issuance"),
    FieldReference("CashDividendsPaid", "cash dividends paid"),
    FieldReference("ChangeInAccountPayable", "change in account payable"),
    FieldReference("SpecialIncomeCharges", "special income charges"),
    FieldReference("OtherSpecialCharges", "other special charges"),
    FieldReference(
        "RestructuringAndMergernAcquisition",
        "restructuring and merger or acquisition charges",
    ),
    FieldReference("ImpairmentOfCapitalAssets", "impairment of capital assets"),
    FieldReference("WriteOff", "write-off charges"),
    FieldReference("SellingAndMarketingExpense", "selling and marketing expense"),
    FieldReference("NetIncome", "net income"),
    FieldReference("TotalRevenue", "total revenue"),
    FieldReference("GrossProfit", "gross profit"),
    FieldReference("OperatingExpense", "operating expense"),
    FieldReference("ResearchAndDevelopment", "research and development expense"),
    FieldReference(
        "SellingGeneralAndAdministration",
        "selling, general, and administrative expense",
    ),
    FieldReference("PretaxIncome", "pretax income"),
    FieldReference("TaxProvision", "tax provision"),
    FieldReference("BasicEPS", "basic EPS"),
    FieldReference("DilutedEPS", "diluted EPS"),
    FieldReference("BasicAverageShares", "basic average shares"),
    FieldReference("DilutedAverageShares", "diluted average shares"),
    FieldReference(
        "NetIncomeContinuousOperations", "net income from continuing operations"
    ),
    FieldReference("CapitalLeaseObligations", "capital lease obligations"),
    FieldReference("TotalDebt", "total debt"),
    FieldReference("NetDebt", "net debt"),
    FieldReference(
        "GoodwillAndOtherIntangibleAssets",
        "goodwill and other intangible assets",
    ),
    FieldReference("Goodwill", "goodwill"),
    FieldReference("AccountsReceivable", "accounts receivable"),
    FieldReference("Inventory", "inventory"),
    FieldReference(
        "CashCashEquivalentsAndShortTermInvestments",
        "cash, cash equivalents, and short-term investments",
    ),
    FieldReference("LongTermDebt", "long-term debt"),
    FieldReference("NetPPE", "net property, plant, and equipment"),
    FieldReference("TotalNonCurrentAssets", "total non-current assets"),
    FieldReference(
        "TotalNonCurrentLiabilitiesNetMinorityInterest",
        "total non-current liabilities net minority interest",
    ),
    FieldReference("InvestedCapital", "invested capital"),
    FieldReference("WorkingCapital", "working capital"),
    FieldReference("TangibleBookValue", "tangible book value"),
)

_TIMESERIES_QUARTERLY_TRAILING_METRICS: tuple[FieldReference, ...] = (
    FieldReference("TotalRevenue", "total revenue"),
    FieldReference("NetIncome", "net income"),
    FieldReference("CostOfRevenue", "cost of revenue"),
    FieldReference("GrossProfit", "gross profit"),
    FieldReference("OperatingIncome", "operating income"),
    FieldReference("InterestExpense", "interest expense"),
    FieldReference("BasicEPS", "basic EPS"),
    FieldReference("DilutedEPS", "diluted EPS"),
    FieldReference("EBITDA", "EBITDA"),
    FieldReference("OperatingExpense", "operating expense"),
    FieldReference("PretaxIncome", "pretax income"),
    FieldReference("TaxProvision", "tax provision"),
    FieldReference("BasicAverageShares", "basic average shares"),
    FieldReference("DilutedAverageShares", "diluted average shares"),
    FieldReference("OtherIncomeExpense", "other income or expense"),
    FieldReference(
        "NetIncomeContinuousOperations", "net income from continuing operations"
    ),
    FieldReference("NormalizedEBITDA", "normalized EBITDA"),
    FieldReference("SellingAndMarketingExpense", "selling and marketing expense"),
    FieldReference(
        "SellingGeneralAndAdministration",
        "selling, general, and administrative expense",
    ),
    FieldReference("ResearchAndDevelopment", "research and development expense"),
)

TIMESERIES_TYPE_REFERENCES: tuple[FieldReference, ...] = (
    *_TIMESERIES_EVENTS,
    *_prefixed_field_references(
        _TIMESERIES_QUARTERLY_TRAILING_PREFIXES,
        _TIMESERIES_VALUATION_METRICS,
    ),
    *_prefixed_field_references(
        _TIMESERIES_ANNUAL_PREFIXES, _TIMESERIES_ANNUAL_METRICS
    ),
    *_prefixed_field_references(
        _TIMESERIES_QUARTERLY_TRAILING_PREFIXES,
        _TIMESERIES_QUARTERLY_TRAILING_METRICS,
    ),
)


QUOTE_FIELDS: tuple[FieldReference, ...] = (
    FieldReference(
        "ask", "Lowest price a seller is willing to accept for the security."
    ),
    FieldReference("askSize", "Number of units available at current ask price."),
    FieldReference(
        "averageAnalystRating",
        "Consensus rating from financial analysts for the quote.",
    ),
    FieldReference(
        "averageDailyVolume10Day",
        "Average number of shares traded each day over the last 10 days.",
    ),
    FieldReference(
        "averageDailyVolume3Month",
        "Average number of shares traded each day over the last 3 months.",
    ),
    FieldReference("bid", "Highest price a buyer is willing to pay for the security."),
    FieldReference(
        "bidSize", "Total number of shares that buyers want to buy at the bid price."
    ),
    FieldReference("bookValue", "Net accounting value of a company's assets."),
    FieldReference(
        "circulatingSupply",
        "Number of cryptocurrency units currently in public circulation.",
    ),
    FieldReference("coinImageUrl", "URL of the image representing the cryptocurrency."),
    FieldReference(
        "coinMarketCapLink", "URL of the MarketCap site for the cryptocurrency."
    ),
    FieldReference("contractSymbol", "Ticker symbol for a futures contract."),
    FieldReference("cryptoTradeable", "Whether the cryptocurrency can be traded."),
    FieldReference(
        "customPriceAlertConfidence", "Undocumented Yahoo price alert confidence value."
    ),
    FieldReference("currency", "Currency in which the security is traded."),
    FieldReference("displayName", "User-friendly name of the quote or security."),
    FieldReference(
        "dividendDate", "Date when the company is expected to pay its next dividend."
    ),
    FieldReference("dividendRate", "Amount of dividends expected over the next year."),
    FieldReference(
        "dividendYield",
        "Annual dividend as a percentage of the security's current price.",
    ),
    FieldReference(
        "earningsTimestamp", "Raw timestamp for the company's earnings announcement."
    ),
    FieldReference(
        "earningsTimestampEnd",
        "Raw timestamp for the end of the earnings announcement window.",
    ),
    FieldReference(
        "earningsTimestampStart",
        "Raw timestamp for the start of the earnings announcement window.",
    ),
    FieldReference(
        "epsCurrentYear", "Company's earnings per share for the current year."
    ),
    FieldReference(
        "epsForward", "Company's projected earnings per share for the next fiscal year."
    ),
    FieldReference(
        "epsTrailingTwelveMonths",
        "Company's earnings per share for the past 12 months.",
    ),
    FieldReference("esgPopulated", "Availability status of ESG ratings data."),
    FieldReference("exchange", "Securities exchange on which the security is traded."),
    FieldReference(
        "exchangeDataDelayedBy",
        "Delay in data from the exchange, typically in minutes.",
    ),
    FieldReference("exchangeTimezoneName", "Name of the exchange timezone."),
    FieldReference("exchangeTimezoneShortName", "Short name of the exchange timezone."),
    FieldReference("expireDate", "Date on which the option contract expires."),
    FieldReference("expireIsoDate", "Option expiration date in ISO 8601 format."),
    FieldReference(
        "fiftyDayAverage", "Average closing price over the past 50 trading days."
    ),
    FieldReference(
        "fiftyDayAverageChange",
        "Change in the 50-day average price from the previous trading day.",
    ),
    FieldReference(
        "fiftyDayAverageChangePercent",
        "Percent change in the 50-day average price from the previous trading day.",
    ),
    FieldReference(
        "fiftyTwoWeekChangePercent",
        "Percentage change in price over the past 52 weeks.",
    ),
    FieldReference("fiftyTwoWeekHigh", "Highest price traded over the past 52 weeks."),
    FieldReference(
        "fiftyTwoWeekHighChange",
        "Change in the 52-week high price from the previous trading day.",
    ),
    FieldReference(
        "fiftyTwoWeekHighChangePercent",
        "Percent change in the 52-week high price from the previous trading day.",
    ),
    FieldReference("fiftyTwoWeekLow", "Lowest price traded over the past 52 weeks."),
    FieldReference(
        "fiftyTwoWeekLowChange",
        "Change in the 52-week low price from the previous trading day.",
    ),
    FieldReference(
        "fiftyTwoWeekLowChangePercent",
        "Percent change in the 52-week low price from the previous trading day.",
    ),
    FieldReference("fiftyTwoWeekRange", "Trading price range over the past 52 weeks."),
    FieldReference(
        "financialCurrency", "Currency in which the company reports financial results."
    ),
    FieldReference(
        "firstTradeDateMilliseconds", "Raw first-trade timestamp in milliseconds."
    ),
    FieldReference(
        "forwardPe", "Projected price-to-earnings ratio for the next 12 months."
    ),
    FieldReference("fromCurrency", "Base currency in an exchange pair."),
    FieldReference("fullExchangeName", "Full name of the securities exchange."),
    FieldReference(
        "gmtOffSetMilliseconds", "Exchange offset from GMT in milliseconds."
    ),
    FieldReference(
        "headSymbolAsString", "Symbol of the contract's underlying security."
    ),
    FieldReference("ipoExpectedDate", "Expected date of the initial public offering."),
    FieldReference("language", "Language in which financial results are reported."),
    FieldReference("lastMarket", "Last market in which the security was traded."),
    FieldReference("logoUrl", "URL of the company's logo."),
    FieldReference("longName", "Official name of the company or security."),
    FieldReference("market", "Primary market for the security."),
    FieldReference(
        "marketCap", "Total market value of the security in trading currency."
    ),
    FieldReference("marketState", "Current state of the market for the security."),
    FieldReference("messageBoardId", "Identifier for the Yahoo Finance message board."),
    FieldReference(
        "morningstarIndustry",
        "Morningstar industry classification when Yahoo returns it.",
    ),
    FieldReference(
        "nameChangeDate", "Date on which the company last changed its name."
    ),
    FieldReference("netAssets", "Total net assets of the fund or company."),
    FieldReference("netExpenseRatio", "Ratio of total expenses to total net assets."),
    FieldReference(
        "openInterest", "Total number of open futures or options contracts."
    ),
    FieldReference("optionType", "Type of option."),
    FieldReference("postMarketChange", "Change in the security's post-market price."),
    FieldReference(
        "postMarketChangePercent", "Percent change in the security's post-market price."
    ),
    FieldReference("postMarketPrice", "Price of the security in post-market trading."),
    FieldReference(
        "postMarketTime", "Raw timestamp of the most recent post-market trade."
    ),
    FieldReference("preMarketChange", "Change in the security's pre-market price."),
    FieldReference(
        "preMarketChangePercent", "Percent change in the security's pre-market price."
    ),
    FieldReference("preMarketPrice", "Price of the security in pre-market trading."),
    FieldReference(
        "preMarketTime", "Raw timestamp of the most recent pre-market trade."
    ),
    FieldReference("prevName", "Company name before its most recent name change."),
    FieldReference("priceEpsCurrentYear", "Current-year price-to-earnings ratio."),
    FieldReference("priceHint", "Decimal precision indicator for price values."),
    FieldReference("priceToBook", "Market value relative to book value per share."),
    FieldReference("quoteSourceName", "Name of the source providing the quote."),
    FieldReference("quoteType", "Type of quote."),
    FieldReference("region", "Region in which the company or security is located."),
    FieldReference(
        "regularMarketChange", "Change in the security's regular-market price."
    ),
    FieldReference(
        "regularMarketChangePercent",
        "Percent change in the security's regular-market price.",
    ),
    FieldReference(
        "regularMarketDayHigh", "Highest price during the regular trading session."
    ),
    FieldReference(
        "regularMarketDayLow", "Lowest price during the regular trading session."
    ),
    FieldReference(
        "regularMarketDayRange", "Price range during the regular trading session."
    ),
    FieldReference(
        "regularMarketOpen", "Opening price for the regular trading session."
    ),
    FieldReference(
        "regularMarketPreviousClose", "Previous regular-session closing price."
    ),
    FieldReference(
        "regularMarketPrice", "Latest price from the regular trading session."
    ),
    FieldReference(
        "regularMarketTime", "Raw timestamp of the most recent regular-session trade."
    ),
    FieldReference(
        "regularMarketVolume", "Number of units traded in the regular session."
    ),
    FieldReference(
        "sharesOutstanding", "Number of shares currently held by shareholders."
    ),
    FieldReference("shortName", "Short user-friendly name for the quote or security."),
    FieldReference(
        "sourceInterval",
        "Interval at which the data source provides updates, in seconds.",
    ),
    FieldReference("startDate", "Date on which the coin started trading."),
    FieldReference("strike", "Contractually specified price for options exercise."),
    FieldReference("symbol", "Ticker symbol of the security."),
    FieldReference("toCurrency", "Counter currency in an exchange pair."),
    FieldReference("tradeable", "Whether the security is currently tradeable."),
    FieldReference(
        "trailingAnnualDividendRate",
        "Dividend payment per share over the past 12 months.",
    ),
    FieldReference(
        "trailingAnnualDividendYield", "Dividend yield over the past 12 months."
    ),
    FieldReference(
        "trailingPE",
        "Trailing price-to-earnings ratio based on past twelve-month results.",
    ),
    FieldReference(
        "trailingThreeMonthNavReturns", "Trailing three-month net asset value returns."
    ),
    FieldReference("trailingThreeMonthReturns", "Trailing three-month returns."),
    FieldReference(
        "triggerable", "Internal Yahoo Finance flag with undocumented purpose."
    ),
    FieldReference(
        "twoHundredDayAverage", "Average closing price over the past 200 trading days."
    ),
    FieldReference(
        "twoHundredDayAverageChange",
        "Change in the 200-day average price from the previous trading day.",
    ),
    FieldReference(
        "twoHundredDayAverageChangePercent",
        "Percent change in the 200-day average price from the previous trading day.",
    ),
    FieldReference("typeDisp", "User-friendly representation of the quote type."),
    FieldReference(
        "underlyingExchangeSymbol",
        "Exchange symbol for the underlying asset's trading venue.",
    ),
    FieldReference(
        "underlyingShortName", "Short name of the underlying derivative security."
    ),
    FieldReference(
        "underlyingSymbol", "Ticker symbol of the underlying derivative security."
    ),
    FieldReference(
        "volume24Hr", "Total cryptocurrency trading volume in the past 24 hours."
    ),
    FieldReference(
        "volumeAllCurrencies",
        "Aggregate 24-hour cryptocurrency volume across currency pairs.",
    ),
    FieldReference("ytdReturn", "Year-to-date return on the security."),
)


QUOTE_COMMAND = CommandSpec(
    name="quote",
    path="/v7/finance/quote",
    summary="Quote data for one or more symbols.",
    description=(
        "Prices, trading state, identity, market data, and optional quote fields "
        "for one or more symbols."
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
    field_reference=QUOTE_FIELDS,
)

OPTIONS_COMMAND = CommandSpec(
    name="options",
    path="/v7/finance/options/{symbol}",
    summary="Option chain data for a single symbol.",
    description=(
        "Expiration chains, contract lists, strikes, implied volatility, and quote "
        "data for one symbol."
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

QUOTE_TYPE_COMMAND = CommandSpec(
    name="quote-type",
    path="/v1/finance/quoteType/",
    summary="Quote type data for a single symbol.",
    description=(
        "Instrument classification, exchange, market, and quote-type metadata for "
        "one symbol."
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

QUOTE_SUMMARY_MODULES: tuple[FieldReference, ...] = (
    FieldReference(
        "assetProfile",
        "Company address, industry, officers, governance, and business summary.",
    ),
    FieldReference("balanceSheetHistory", "Annual balance sheet statements."),
    FieldReference(
        "balanceSheetHistoryQuarterly", "Quarterly balance sheet statements."
    ),
    FieldReference(
        "calendarEvents",
        "Earnings dates, ex-dividend date, and related calendar data.",
    ),
    FieldReference("cashflowStatementHistory", "Annual cash flow statements."),
    FieldReference(
        "cashflowStatementHistoryQuarterly", "Quarterly cash flow statements."
    ),
    FieldReference(
        "defaultKeyStatistics",
        "Valuation, share-count, short-interest, and per-share statistics.",
    ),
    FieldReference("earnings", "Earnings charts and annual financial summaries."),
    FieldReference("earningsHistory", "Historical EPS estimate and surprise data."),
    FieldReference("earningsTrend", "Analyst earnings and revenue estimate trends."),
    FieldReference(
        "equityPerformance", "Equity performance overview and peer context."
    ),
    FieldReference(
        "financialData",
        "Analyst targets, recommendation data, margins, cash, debt, and growth fields.",
    ),
    FieldReference("fundOwnership", "Institutional fund ownership records."),
    FieldReference(
        "fundPerformance",
        "Fund returns, risk statistics, and performance category comparisons.",
    ),
    FieldReference(
        "fundProfile", "Fund family, category, fees, expenses, and management details."
    ),
    FieldReference("incomeStatementHistory", "Annual income statements."),
    FieldReference("incomeStatementHistoryQuarterly", "Quarterly income statements."),
    FieldReference("indexTrend", "Index-level earnings trend context."),
    FieldReference("industryTrend", "Industry-level earnings trend context."),
    FieldReference("insiderHolders", "Current insider holder records."),
    FieldReference("insiderTransactions", "Insider purchase and sale transactions."),
    FieldReference("institutionOwnership", "Institutional ownership records."),
    FieldReference("majorDirectHolders", "Major direct holder records."),
    FieldReference(
        "majorHoldersBreakdown",
        "Insider, institution, and float ownership percentages.",
    ),
    FieldReference("netSharePurchaseActivity", "Insider net share purchase activity."),
    FieldReference(
        "price",
        "Current price, exchange, currency, market state, and quote source data.",
    ),
    FieldReference(
        "quoteType", "Instrument type, exchange, timezone, and symbol identity."
    ),
    FieldReference("recommendationTrend", "Analyst recommendation trend counts."),
    FieldReference("secFilings", "Recent SEC filing metadata."),
    FieldReference("sectorTrend", "Sector-level earnings trend context."),
    FieldReference(
        "summaryDetail", "Market summary, dividend, volume, beta, and valuation fields."
    ),
    FieldReference(
        "summaryProfile",
        "Business summary, sector, industry, employees, and website.",
    ),
    FieldReference("topHoldings", "Fund holdings, sector weights, and bond ratings."),
    FieldReference("upgradeDowngradeHistory", "Analyst upgrade and downgrade history."),
)

QUOTE_SUMMARY_COMMAND = CommandSpec(
    name="quote-summary",
    path="/v10/finance/quoteSummary/{symbol}",
    summary="Quote summary modules for a single symbol.",
    description=(
        "Selected modules such as price, profile, financial data, earnings, "
        "statistics, and holder details for one symbol."
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
    field_reference=QUOTE_SUMMARY_MODULES,
    field_reference_title="Quote summary --modules reference",
    notes=(
        "Module availability depends on instrument type.",
        "Live AAPL probe populated the equity-focused modules.",
        "Live VT probe populated fundProfile, fundPerformance, and topHoldings.",
    ),
)

PRICE_INSIGHTS_COMMAND = CommandSpec(
    name="price-insights",
    path="/ws/company-fundamentals/v1/finance/price-insights",
    summary="Generated price insight data for one or more symbols.",
    description=(
        "News, AI analysis, anomaly checks, and analyst-rating context for one or "
        "more symbols when available."
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

CALENDAR_EVENTS_COMMAND = CommandSpec(
    name="calendar-events",
    path="/ws/screeners/v1/finance/calendar-events",
    summary="Calendar events for a single symbol.",
    description=(
        "Calendar event data such as earnings events for one symbol, with "
        "optional economic-event filters when Yahoo supports them."
    ),
    use_crumb=True,
    params=(
        ParamSpec(
            name="tickersFilter",
            cli_name="symbol",
            kind=ParamKind.STRING,
            positional=True,
            required=True,
            metavar="SYMBOL",
            help="A single Yahoo symbol, such as AAPL or SHOP.TO.",
        ),
        ParamSpec(
            name="modules",
            cli_name="modules",
            kind=ParamKind.CSV,
            default="earnings",
            metavar="MODULE[,MODULE...]",
            min_items=1,
            help=(
                "Comma-separated Yahoo calendar event modules to request. "
                "Observed value: earnings. Yogurt does not validate module names."
            ),
        ),
        ParamSpec(
            name="countPerDay",
            cli_name="count-per-day",
            kind=ParamKind.INTEGER,
            default=100,
            metavar="COUNT",
            help="Maximum calendar event rows to request per day.",
        ),
        ParamSpec(
            name="startDate",
            cli_name="start-date",
            kind=ParamKind.DATETIME_MILLISECONDS,
            default="now-3d",
            metavar="DATE",
            help=(
                "Start date as Unix seconds, Unix milliseconds, YYYY-MM-DD date, "
                "or ISO datetime. Yogurt sends milliseconds to Yahoo."
            ),
        ),
        ParamSpec(
            name="endDate",
            cli_name="end-date",
            kind=ParamKind.DATETIME_MILLISECONDS,
            default="now",
            metavar="DATE",
            help=(
                "End date as Unix seconds, Unix milliseconds, YYYY-MM-DD date, "
                "or ISO datetime. Yogurt sends milliseconds to Yahoo."
            ),
        ),
        ParamSpec(
            name="economicEventsHighImportanceOnly",
            cli_name="economic-events-high-importance-only",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request only high-importance economic events when Yahoo supports it.",
        ),
        ParamSpec(
            name="economicEventsRegionFilter",
            cli_name="economic-events-region-filter",
            kind=ParamKind.STRING,
            default="",
            allow_empty_default=True,
            metavar="REGION",
            help=(
                "Economic event region filter. Observed Yahoo requests send an "
                "empty value. Defaults to an empty value when omitted."
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
        "yogurt calendar-events AAPL",
        (
            "yogurt calendar-events AAPL --start-date 2026-05-01 "
            "--end-date 2026-05-04 --count-per-day 100"
        ),
        (
            "yogurt calendar-events AAPL --start-date 1777593600000 "
            "--end-date 1777852800000 --modules earnings"
        ),
    ),
    common_modules=("earnings",),
    notes=(
        "startDate and endDate are sent to Yahoo as milliseconds.",
        "The --modules parameter is open-ended; observed useful value is earnings.",
        (
            "Observed Yahoo requests include economic event filters even when "
            "requesting earnings."
        ),
    ),
)

FUNDAMENTALS_TIMESERIES_COMMAND = CommandSpec(
    name="timeseries",
    path="/ws/fundamentals-timeseries/v1/finance/timeseries/{symbol}",
    summary="Fundamentals timeseries data for a single symbol.",
    description=(
        "Timestamped fundamentals, valuation ratios, earnings events, analyst "
        "ratings, and economic events for one symbol."
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
            default="now-3d",
            metavar="DATE",
            help=(
                "Start date as a Unix timestamp, YYYY-MM-DD date, or ISO "
                "datetime. Defaults to a recent quote-page window when omitted. "
                "Date-only values are converted at UTC midnight."
            ),
        ),
        ParamSpec(
            name="period2",
            cli_name="period2",
            kind=ParamKind.DATETIME,
            default="now",
            metavar="DATE",
            help=(
                "End date as a Unix timestamp, YYYY-MM-DD date, or ISO "
                "datetime. Defaults to the current Unix timestamp when omitted. "
                "Date-only values are converted at UTC midnight."
            ),
        ),
        ParamSpec(
            name="merge",
            cli_name="merge",
            kind=ParamKind.BOOLEAN,
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
        "yogurt timeseries AAPL",
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
    field_reference=TIMESERIES_TYPE_REFERENCES,
    field_reference_title="Timeseries --type reference",
    notes=(
        "The --type parameter is open-ended; availability depends on symbol.",
        (
            "period1 and period2 accept Unix timestamps, YYYY-MM-DD dates, "
            "or ISO datetimes."
        ),
        (
            "When period arguments are omitted, Yogurt requests a recent "
            "quote-page-style window ending at the current Unix timestamp."
        ),
    ),
)

INSIGHTS_COMMAND = CommandSpec(
    name="insights",
    path="/ws/insights/v3/finance/insights",
    summary="Insight data for one or more symbols.",
    description=(
        "Research report metadata, company snapshots, and instrument insights for "
        "one or more symbols when available."
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

PREDEFINED_SCREENER_COMMAND = CommandSpec(
    name="predefined-screener",
    path="/v1/finance/screener/predefined/saved",
    summary="Predefined Yahoo screener results.",
    description=(
        "Records from Yahoo's predefined saved screeners, such as most-active "
        "symbols, with caller-selected quote fields."
    ),
    use_crumb=True,
    params=(
        ParamSpec(
            name="scrIds",
            cli_name="scr-ids",
            kind=ParamKind.CSV,
            positional=True,
            required=True,
            metavar="SCR_ID[,SCR_ID...]",
            min_items=1,
            help=(
                "One or more comma-separated Yahoo predefined screener IDs, "
                "such as MOST_ACTIVES."
            ),
        ),
        ParamSpec(
            name="count",
            cli_name="count",
            kind=ParamKind.INTEGER,
            default=200,
            metavar="COUNT",
            help="Number of screener records to request.",
        ),
        ParamSpec(
            name="start",
            cli_name="start",
            kind=ParamKind.INTEGER,
            default=0,
            metavar="OFFSET",
            help="Zero-based record offset for paging through screener results.",
        ),
        ParamSpec(
            name="fields",
            cli_name="fields",
            kind=ParamKind.CSV,
            default="symbol,shortName",
            metavar="FIELD[,FIELD...]",
            help=(
                "Comma-separated Yahoo quote fields to include in screener "
                "records. Yogurt does not validate field names."
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
            name="useRecordsResponse",
            cli_name="use-records-response",
            kind=ParamKind.BOOLEAN,
            default=True,
            metavar="BOOL",
            help="Request Yahoo's records-style screener response shape.",
        ),
        ParamSpec(
            name="sortField",
            cli_name="sort-field",
            kind=ParamKind.STRING,
            default="",
            allow_empty_default=True,
            metavar="FIELD",
            help=(
                "Optional Yahoo sort field. Omit it for Yahoo's observed empty "
                "sortField."
            ),
        ),
        ParamSpec(
            name="sortType",
            cli_name="sort-type",
            kind=ParamKind.STRING,
            default="",
            allow_empty_default=True,
            metavar="TYPE",
            help=(
                "Optional Yahoo sort direction/type. Omit it for Yahoo's "
                "observed empty sortType."
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
        "yogurt predefined-screener MOST_ACTIVES",
        "yogurt predefined-screener MOST_ACTIVES --count 25 --start 25",
        (
            "yogurt predefined-screener MOST_ACTIVES "
            "--fields symbol,shortName,regularMarketPrice,regularMarketVolume"
        ),
    ),
    field_reference=QUOTE_FIELDS,
    field_reference_title="Predefined screener --fields reference",
    notes=(
        "Screener IDs are Yahoo-defined and open-ended; Yogurt does not validate them.",
        (
            "Observed Yahoo quote pages request MOST_ACTIVES with count=200, "
            "start=0, fields=symbol,shortName, formatted=true, and "
            "useRecordsResponse=true."
        ),
        (
            "Observed browser requests include empty sortField and sortType; "
            "Yogurt sends those empty values when the options are omitted."
        ),
    ),
)

CHART_COMMAND = CommandSpec(
    name="chart",
    path="/v8/finance/chart/{symbol}",
    summary="Chart price data for a single symbol.",
    description=(
        "Calls Yahoo Finance's chart endpoint for one symbol and writes the "
        "response body to stdout without formatting or response-model mapping."
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
            help="A single Yahoo symbol, such as AAPL, GC=F, SPY, or BTC-USD.",
        ),
        ParamSpec(
            name="period1",
            cli_name="period1",
            kind=ParamKind.DATETIME,
            default="now-3d",
            metavar="DATE",
            help=(
                "Start date as a Unix timestamp, YYYY-MM-DD date, or ISO "
                "datetime. Defaults to a recent quote-page window when omitted. "
                "Date-only values are converted at UTC midnight."
            ),
        ),
        ParamSpec(
            name="period2",
            cli_name="period2",
            kind=ParamKind.DATETIME,
            default="now",
            metavar="DATE",
            help=(
                "End date as a Unix timestamp, YYYY-MM-DD date, or ISO "
                "datetime. Defaults to the current Unix timestamp when omitted. "
                "Date-only values are converted at UTC midnight."
            ),
        ),
        ParamSpec(
            name="interval",
            cli_name="interval",
            kind=ParamKind.STRING,
            default="1m",
            metavar="INTERVAL",
            help=("Chart interval. Supported values: 1m, 5m, 15m, 1d, 1wk, 1mo."),
        ),
        ParamSpec(
            name="includePrePost",
            cli_name="include-pre-post",
            kind=ParamKind.BOOLEAN,
            default=False,
            metavar="BOOL",
            help="Include pre-market and post-market data when Yahoo supports it.",
        ),
        ParamSpec(
            name="events",
            cli_name="events",
            kind=ParamKind.CSV,
            default="div,split,earn",
            metavar="EVENT[,EVENT...]",
            allowed_values=("div", "split", "earn"),
            csv_separator="|",
            help=(
                "Comma-separated chart events to request. Supported values: "
                "div, split, earn."
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
        "yogurt chart AAPL",
        "yogurt chart AAPL --period1 2026-04-30",
        "yogurt chart AAPL --period1 1777507200 --period2 1777593600 --interval 1m",
        "yogurt chart SPY --period1 2026-01-01 --interval 1d --events div,split",
    ),
    notes=(
        "period2 must be greater than period1.",
        (
            "When period2 is omitted, Yogurt sends the current Unix timestamp; "
            "now is not accepted as a user-provided value."
        ),
        (
            "Yahoo can reject overlong short-interval windows for 1m, 5m, and 15m "
            "intervals."
        ),
        (
            "Live probes across several symbol types returned the observed chart "
            "payload without additional query parameters."
        ),
    ),
)

RATINGS_TOP_COMMAND = CommandSpec(
    name="ratings-top",
    path="/v2/ratings/top/{symbol}",
    summary="Top analyst rating scores for a single symbol.",
    description=("Top analyst rating buckets and score components for one symbol."),
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

COMMANDS: tuple[CommandSpec, ...] = (
    QUOTE_COMMAND,
    OPTIONS_COMMAND,
    QUOTE_TYPE_COMMAND,
    QUOTE_SUMMARY_COMMAND,
    PRICE_INSIGHTS_COMMAND,
    CALENDAR_EVENTS_COMMAND,
    FUNDAMENTALS_TIMESERIES_COMMAND,
    INSIGHTS_COMMAND,
    PREDEFINED_SCREENER_COMMAND,
    CHART_COMMAND,
    RATINGS_TOP_COMMAND,
)
COMMANDS_BY_NAME: dict[str, CommandSpec] = {
    command.name: command for command in COMMANDS
}
