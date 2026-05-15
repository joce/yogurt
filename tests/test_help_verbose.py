"""Tests for per-command --help-verbose, which appends reference docs."""

from __future__ import annotations

from importlib.resources import files

import pytest

from yogurt.cli import main

_DOCS_DIR = "yogurt.docs"
_DOC_MARKER_LINE = 10
_ARGPARSE_ERROR_EXIT = 2

_VERBOSE_HELP_COMMANDS: tuple[tuple[str, str], ...] = (
    ("screener", "QUERY_DSL.md"),
    ("visualization", "QUERY_DSL.md"),
)


@pytest.mark.parametrize(("command", "doc_filename"), _VERBOSE_HELP_COMMANDS)
def test_help_verbose_appends_reference_doc(
    command: str,
    doc_filename: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`<command> --help-verbose` prints standard help followed by the doc."""

    expected_doc = (files(_DOCS_DIR) / doc_filename).read_text(encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        main([command, "--help-verbose"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    # Standard help still present (usage line).
    assert f"usage: yogurt {command}" in captured.out
    # Doc body appended verbatim.
    assert expected_doc.rstrip() in captured.out


@pytest.mark.parametrize(("command", "_doc_filename"), _VERBOSE_HELP_COMMANDS)
def test_help_mentions_help_verbose(
    command: str,
    _doc_filename: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Standard `--help` for verbose-enabled commands points to --help-verbose."""

    with pytest.raises(SystemExit) as exc_info:
        main([command, "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "--help-verbose" in captured.out


@pytest.mark.parametrize(("command", "doc_filename"), _VERBOSE_HELP_COMMANDS)
def test_standard_help_does_not_include_doc_body(
    command: str,
    doc_filename: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Standard `--help` does NOT dump the full reference doc."""

    expected_doc = (files(_DOCS_DIR) / doc_filename).read_text(encoding="utf-8")
    # Pick a marker far enough into the doc that it would not be in a brief
    # mention.
    lines = expected_doc.splitlines()
    marker = lines[_DOC_MARKER_LINE] if len(lines) > _DOC_MARKER_LINE else ""
    if not marker.strip():
        return

    with pytest.raises(SystemExit) as exc_info:
        main([command, "--help"])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert marker not in captured.out


@pytest.mark.parametrize(
    "command",
    ["raw", "quote", "quote-summary", "timeseries"],
)
def test_unaffected_command_has_no_help_verbose(
    command: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Commands without an associated DSL doc do not expose --help-verbose.

    Quote, quote-summary, and timeseries already publish their full
    field/module references in the standard --help epilog, so they should not
    duplicate the same content behind a verbose-help flag.
    """

    args = (
        [command, "AAPL", "--help-verbose"]
        if command != "raw"
        else [
            command,
            "/v7/finance/quote",
            "--help-verbose",
        ]
    )
    with pytest.raises(SystemExit) as exc_info:
        main(args)

    # argparse exits 2 on unrecognized argument.
    assert exc_info.value.code == _ARGPARSE_ERROR_EXIT
    captured = capsys.readouterr()
    assert "unrecognized arguments" in captured.err or "error" in captured.err
