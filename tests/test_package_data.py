"""Verify reference docs ship as importable package data."""

from __future__ import annotations

from importlib.resources import files


def test_docs_directory_contains_expected_files() -> None:
    """The yogurt.docs package exposes the four reference markdown files."""

    expected = {
        "QUERY_DSL.md",
        "QUOTE_FIELDS.md",
        "QUOTE_SUMMARY_MODULES.md",
        "TIMESERIES_TYPES.md",
    }
    present = {p.name for p in files("yogurt.docs").iterdir() if p.name.endswith(".md")}
    assert expected <= present


def test_docs_are_readable() -> None:
    """Each reference doc is readable as UTF-8 text with its expected heading."""

    cases = {
        "QUERY_DSL.md": "# Query DSL",
        "QUOTE_FIELDS.md": "# Quote",
        "QUOTE_SUMMARY_MODULES.md": "# Quote",
        "TIMESERIES_TYPES.md": "# Timeseries",
    }
    for name, heading in cases.items():
        text = (files("yogurt.docs") / name).read_text(encoding="utf-8")
        assert text.startswith(heading), f"{name} should start with {heading!r}"
