"""Tests for parameter coercion."""

from __future__ import annotations

import pytest

from yoghurt.params import (
    ParamKind,
    ParamSpec,
    coerce_param,
    parse_boolean,
    parse_datetime,
)

IMAGE_SIZE = 50
NOV_17_2017 = 1510876800
NOV_17_2017_MS = NOV_17_2017 * 1000


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param("true", True, id="true"),
        pytest.param("false", False, id="false"),
        pytest.param("1", True, id="one"),
        pytest.param("0", False, id="zero"),
    ],
)
def test_parse_boolean_accepts_common_values(value: str, expected: object) -> None:
    """Common CLI boolean spellings are accepted."""

    assert parse_boolean(value) is expected


def test_parse_boolean_rejects_invalid_value() -> None:
    """Invalid boolean text raises a clear error."""

    with pytest.raises(ValueError, match="expected boolean"):
        parse_boolean("maybe")


def test_coerce_param_rejects_empty_strings() -> None:
    """String-like endpoint params cannot be empty."""

    spec = ParamSpec("symbols", "symbols", ParamKind.CSV, "Ticker symbols")

    with pytest.raises(ValueError, match="cannot be empty"):
        coerce_param(spec, " ")


def test_coerce_param_parses_integer() -> None:
    """Integer endpoint params are parsed to int."""

    spec = ParamSpec("imgWidths", "img-widths", ParamKind.INTEGER, "Width")

    assert coerce_param(spec, "50") == IMAGE_SIZE


@pytest.mark.parametrize(
    "value",
    [
        pytest.param("1510876800", id="unix-timestamp"),
        pytest.param("2017-11-17", id="yahoo-date"),
        pytest.param("2017-11-17T00:00:00+00:00", id="iso-aware"),
        pytest.param("2017-11-17T00:00:00", id="iso-naive"),
    ],
)
def test_parse_datetime_accepts_supported_date_forms(value: str) -> None:
    """Datetime parser accepts timestamps, US dates, and ISO datetimes."""

    assert parse_datetime(value) == NOV_17_2017


def test_parse_datetime_rejects_invalid_date() -> None:
    """Datetime parser rejects unsupported date text."""

    with pytest.raises(ValueError, match="expected Unix timestamp"):
        parse_datetime("17-11-2017")


def test_coerce_param_parses_datetime_kind() -> None:
    """Datetime endpoint params are converted to Unix timestamps."""

    spec = ParamSpec("date", "date", ParamKind.DATETIME, "Expiration date")

    assert coerce_param(spec, "2017-11-17") == NOV_17_2017


def test_parse_datetime_milliseconds_accepts_supported_date_forms() -> None:
    """Millisecond datetime params preserve Yahoo's expected unit."""

    spec = ParamSpec(
        "startDate",
        "start-date",
        ParamKind.DATETIME_MILLISECONDS,
        "Start date",
    )

    assert coerce_param(spec, "2017-11-17") == NOV_17_2017_MS


def test_parse_datetime_milliseconds_converts_unix_seconds() -> None:
    """Unix-second timestamps are converted to milliseconds."""

    spec = ParamSpec(
        "startDate",
        "start-date",
        ParamKind.DATETIME_MILLISECONDS,
        "Start date",
    )

    assert coerce_param(spec, "1510876800") == NOV_17_2017_MS


def test_parse_datetime_milliseconds_accepts_iso_datetime() -> None:
    """ISO datetimes are converted to UTC milliseconds."""

    spec = ParamSpec(
        "startDate",
        "start-date",
        ParamKind.DATETIME_MILLISECONDS,
        "Start date",
    )

    assert coerce_param(spec, "2017-11-17T00:00:00Z") == NOV_17_2017_MS


def test_parse_datetime_milliseconds_preserves_integer_milliseconds() -> None:
    """Already-millisecond integer values are passed through unchanged."""

    spec = ParamSpec(
        "endDate",
        "end-date",
        ParamKind.DATETIME_MILLISECONDS,
        "End date",
    )

    assert coerce_param(spec, "1510876800000") == NOV_17_2017_MS


def test_coerce_csv_param_validates_allowed_values() -> None:
    """CSV params can constrain each requested value."""

    spec = ParamSpec(
        "events",
        "events",
        ParamKind.CSV,
        "Chart events",
        allowed_values=("div", "split", "earn"),
    )

    with pytest.raises(ValueError, match="unsupported value 'foo'"):
        coerce_param(spec, "div,foo")


def test_coerce_csv_param_can_pack_with_custom_separator() -> None:
    """CSV params can be packed for Yahoo without exposing the wire separator."""

    spec = ParamSpec(
        "events",
        "events",
        ParamKind.CSV,
        "Chart events",
        csv_separator="|",
    )

    assert coerce_param(spec, "div, split,earn") == "div|split|earn"
