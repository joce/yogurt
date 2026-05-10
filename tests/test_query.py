"""Tests for the SQL-flavored query parser."""

from __future__ import annotations

import pytest

from yogurt.query import QueryError, parse

EARNINGS_LIMIT = 25
PERATIO_THRESHOLD = 30
LIMIT_PAGE_SIZE = 10
LIMIT_OFFSET = 25


def test_select_compiles_to_visualization_body() -> None:
    """SELECT compiles to Yahoo's visualization-route body shape."""

    body = parse("""
        SELECT ticker, companyshortname, startdatetime,
               epsestimate, epsactual, epssurprisepct, intradaymarketcap
        FROM sp_earnings
        WHERE region = 'us'
          AND startdatetime BETWEEN '2026-05-09' AND '2026-05-16'
          AND eventtype IN ('EAD', 'ERA')
          AND exchange NOT IN ('PNK','OQB','OQX','OEM','OGM','XXX')
        ORDER BY intradaymarketcap DESC
        LIMIT 25
        """).to_body()

    assert body["entityIdType"] == "sp_earnings"
    assert body["sortField"] == "intradaymarketcap"
    assert body["sortType"] == "DESC"
    assert body["size"] == EARNINGS_LIMIT
    assert body["topOperator"] == "AND"
    assert body["includeFields"] == [
        "ticker",
        "companyshortname",
        "startdatetime",
        "epsestimate",
        "epsactual",
        "epssurprisepct",
        "intradaymarketcap",
    ]
    assert body["query"] == {
        "operator": "and",
        "operands": [
            {"operator": "eq", "operands": ["region", "us"]},
            {
                "operator": "btwn",
                "operands": ["startdatetime", "2026-05-09", "2026-05-16"],
            },
            {
                "operator": "or",
                "operands": [
                    {"operator": "eq", "operands": ["eventtype", "EAD"]},
                    {"operator": "eq", "operands": ["eventtype", "ERA"]},
                ],
            },
            {
                "operator": "must_not",
                "operands": [
                    {
                        "operator": "or",
                        "operands": [
                            {"operator": "eq", "operands": ["exchange", "PNK"]},
                            {"operator": "eq", "operands": ["exchange", "OQB"]},
                            {"operator": "eq", "operands": ["exchange", "OQX"]},
                            {"operator": "eq", "operands": ["exchange", "OEM"]},
                            {"operator": "eq", "operands": ["exchange", "OGM"]},
                            {"operator": "eq", "operands": ["exchange", "XXX"]},
                        ],
                    }
                ],
            },
        ],
    }


def test_select_star_omits_include_fields() -> None:
    """SELECT * keeps Yahoo's default column set by omitting includeFields."""

    body = parse("SELECT * FROM sp_earnings WHERE region = 'us'").to_body()

    assert "includeFields" not in body


def test_aggregate_emits_aggregation_block() -> None:
    """AGGREGATE produces date_hist, joinField, fillNA, and entity arrays."""

    body = parse("""
        AGGREGATE date_hist(startdatetime, '1d')
        FROM sp_earnings, economic_event, splits, ipo_info
        WHERE startdatetime BETWEEN '2026-05-03' AND '2026-05-09'
        JOIN BY startdatetime
        FILL pad
        """).to_body()

    assert body["entityIdType"] == [
        "sp_earnings",
        "economic_event",
        "splits",
        "ipo_info",
    ]
    assert body["aggregation"] == {
        "operator": "date_hist",
        "operands": [
            {"operator": "eq", "operands": ["field", "startdatetime"]},
            {"operator": "eq", "operands": ["interval", "1d"]},
        ],
    }
    assert body["joinField"] == "startdatetime"
    assert body["fillNA"] == "pad"
    assert "includeFields" not in body


def test_quote_type_auto_picked_for_uppercase_entity() -> None:
    """A single uppercase bareword entity is sent as quoteType."""

    body = parse("SELECT ticker FROM EQUITY WHERE region = 'us'").to_body()

    assert body["quoteType"] == "EQUITY"
    assert "entityIdType" not in body


def test_entity_id_type_used_for_mixed_or_underscored_names() -> None:
    """Mixed-case or underscored entities flow through entityIdType."""

    body = parse("SELECT ticker FROM INSIDER_TRANSACTION").to_body()

    assert body["entityIdType"] == "INSIDER_TRANSACTION"
    assert "quoteType" not in body


def test_order_by_defaults_direction_to_unspecified() -> None:
    """Omitting ASC/DESC leaves Yahoo to apply its server-side default."""

    body = parse("SELECT ticker FROM sp_earnings ORDER BY startdatetime").to_body()

    assert body["sortField"] == "startdatetime"
    assert "sortType" not in body


def test_order_by_ascending_emits_asc() -> None:
    """ASC is encoded explicitly when the user asks for it."""

    body = parse("SELECT ticker FROM sp_earnings ORDER BY ticker ASC").to_body()

    assert body["sortType"] == "ASC"


def test_in_compiles_to_or_of_eq() -> None:
    """IN is sugar for an OR cluster of eq predicates."""

    body = parse(
        "SELECT ticker FROM sp_earnings WHERE eventtype IN ('EAD', 'ERA')"
    ).to_body()

    assert body["query"] == {
        "operator": "or",
        "operands": [
            {"operator": "eq", "operands": ["eventtype", "EAD"]},
            {"operator": "eq", "operands": ["eventtype", "ERA"]},
        ],
    }


def test_not_in_wraps_or_with_must_not() -> None:
    """NOT IN compiles to must_not(or(eq, eq, ...))."""

    body = parse(
        "SELECT ticker FROM sp_earnings WHERE exchange NOT IN ('PNK','OQB')"
    ).to_body()

    assert body["query"] == {
        "operator": "must_not",
        "operands": [
            {
                "operator": "or",
                "operands": [
                    {"operator": "eq", "operands": ["exchange", "PNK"]},
                    {"operator": "eq", "operands": ["exchange", "OQB"]},
                ],
            }
        ],
    }


def test_not_equal_uses_must_not_eq() -> None:
    """Field != value compiles to must_not(eq(...))."""

    body = parse("SELECT ticker FROM sp_earnings WHERE region != 'us'").to_body()

    assert body["query"] == {
        "operator": "must_not",
        "operands": [{"operator": "eq", "operands": ["region", "us"]}],
    }


def test_comparison_operators_mapped() -> None:
    """gt/gte/lt/lte have explicit operator names."""

    body = parse("""
        SELECT ticker
        FROM EQUITY
        WHERE intradaymarketcap >= 10e9
          AND intradaymarketcap < 50e9
          AND peratio.lasttwelvemonths > 0
          AND peratio.lasttwelvemonths <= 30
        """).to_body()

    operands = body["query"]["operands"]
    operators = [operand["operator"] for operand in operands]
    assert operators == ["gte", "lt", "gt", "lte"]


def test_dotted_field_identifiers_supported() -> None:
    """Field identifiers may include dots, matching Yahoo's namespacing."""

    body = parse(
        "SELECT peratio.lasttwelvemonths FROM EQUITY "
        "WHERE peratio.lasttwelvemonths < 30"
    ).to_body()

    assert body["includeFields"] == ["peratio.lasttwelvemonths"]
    assert body["query"]["operands"][1] == PERATIO_THRESHOLD


def test_explicit_parentheses_force_grouping() -> None:
    """Parenthesized OR sub-expression is preserved inside the AND tree."""

    body = parse("""
        SELECT ticker
        FROM sp_earnings
        WHERE region = 'us'
          AND (eventtype = 'EAD' OR eventtype = 'ERA')
        """).to_body()

    operands = body["query"]["operands"]
    assert operands[0] == {"operator": "eq", "operands": ["region", "us"]}
    assert operands[1] == {
        "operator": "or",
        "operands": [
            {"operator": "eq", "operands": ["eventtype", "EAD"]},
            {"operator": "eq", "operands": ["eventtype", "ERA"]},
        ],
    }


def test_multi_field_order_by_is_rejected() -> None:
    """Yahoo's sortField is a scalar; multi-field ORDER BY must error."""

    with pytest.raises(QueryError, match="single field"):
        parse("SELECT ticker FROM sp_earnings ORDER BY a, b")


def test_aggregate_with_order_by_is_rejected() -> None:
    """ORDER BY does not apply to AGGREGATE statements."""

    with pytest.raises(QueryError, match="ORDER BY"):
        parse(
            "AGGREGATE date_hist(startdatetime, '1d') "
            "FROM sp_earnings ORDER BY startdatetime"
        )


def test_aggregate_only_supports_date_hist() -> None:
    """Other aggregation functions are not supported."""

    with pytest.raises(QueryError, match="Unsupported aggregation"):
        parse("AGGREGATE histogram(price, '1d') FROM sp_earnings")


def test_unterminated_string_literal_raises() -> None:
    """Tokenizer reports unterminated single-quoted strings."""

    with pytest.raises(QueryError, match="Unterminated string"):
        parse("SELECT ticker FROM sp_earnings WHERE region = 'us")


def test_missing_from_clause_raises() -> None:
    """A statement with no FROM is invalid."""

    with pytest.raises(QueryError):
        parse("SELECT ticker WHERE region = 'us'")


def test_join_by_outside_aggregate_raises() -> None:
    """JOIN BY is reserved for AGGREGATE."""

    with pytest.raises(QueryError, match="JOIN BY"):
        parse(
            "SELECT ticker FROM sp_earnings WHERE region = 'us' JOIN BY startdatetime"
        )


def test_limit_offset_round_trip() -> None:
    """LIMIT and OFFSET map to size and offset."""

    body = parse("SELECT ticker FROM sp_earnings LIMIT 10 OFFSET 25").to_body()

    assert body["size"] == LIMIT_PAGE_SIZE
    assert body["offset"] == LIMIT_OFFSET


def test_empty_where_yields_match_all_default() -> None:
    """Omitting WHERE produces an empty AND tree which Yahoo reads as match-all."""

    body = parse("SELECT ticker FROM sp_earnings").to_body()

    assert body["query"] == {"operator": "and", "operands": []}
