"""Command-line interface for Yogurt."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path
from string import Formatter
from typing import TYPE_CHECKING, Final, Protocol, TextIO
from urllib.parse import quote

from typing_extensions import override

from yogurt import __version__
from yogurt.client import YahooClient
from yogurt.commands import COMMANDS, COMMANDS_BY_NAME, CommandSpec, FieldReference
from yogurt.exceptions import YogurtError
from yogurt.params import ParamKind, ParamSpec, coerce_param

if TYPE_CHECKING:
    from collections.abc import Sequence

    from yogurt.types import ParamValue

_THREE_DAYS_SECONDS = 3 * 24 * 60 * 60
_HELP_WIDTH = 100
_HELP_MAX_POSITION = 32
_REFERENCE_INDENT = "  "
_REFERENCE_LABEL_WIDTH = _HELP_MAX_POSITION - len(_REFERENCE_INDENT) - 2
_DATE_PAIR_NAMES: Final[dict[str, tuple[str, str]]] = {
    "chart": ("period1", "period2"),
    "timeseries": ("period1", "period2"),
    "calendar-events": ("startDate", "endDate"),
}


class _YahooClientProtocol(Protocol):
    async def get(
        self,
        path: str,
        params: dict[str, ParamValue],
        *,
        use_crumb: bool = True,
    ) -> str: ...

    async def aclose(self) -> None: ...


class _HelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter,
):
    def __init__(self, prog: str) -> None:
        """Initialize a stable-width formatter for LLM-readable help."""

        super().__init__(prog, max_help_position=_HELP_MAX_POSITION, width=_HELP_WIDTH)

    @override
    def _get_help_string(self, action: argparse.Action) -> str:
        help_text = action.help
        if help_text is None:
            help_text = ""
        if action.default is argparse.SUPPRESS or action.default is None:
            return help_text
        if "%(default)" in help_text:
            return help_text
        return f"{help_text} (default: %(default)s)"


def _add_help_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
    )


def _examples_text(examples: tuple[str, ...]) -> str:
    return "\n".join(f"  {example}" for example in examples)


def _reference_text(references: tuple[FieldReference, ...]) -> str:
    lines: list[str] = []
    description_indent = " " * _HELP_MAX_POSITION
    for field in references:
        label = f"{field.name}:"
        if len(label) <= _REFERENCE_LABEL_WIDTH:
            first_prefix = f"{_REFERENCE_INDENT}{label:<{_REFERENCE_LABEL_WIDTH}}  "
            lines.extend(
                textwrap.wrap(
                    field.description,
                    width=_HELP_WIDTH,
                    initial_indent=first_prefix,
                    subsequent_indent=description_indent,
                )
            )
            continue
        lines.append(f"{_REFERENCE_INDENT}{label}")
        lines.extend(
            textwrap.wrap(
                field.description,
                width=_HELP_WIDTH,
                initial_indent=description_indent,
                subsequent_indent=description_indent,
            )
        )
    return "\n".join(lines)


def _epilog_for_command(command: CommandSpec) -> str:
    field_reference = ""
    if command.field_reference:
        field_reference = (
            f"\n\n{command.field_reference_title}:\n"
            f"{_reference_text(command.field_reference)}"
        )
    reference_sections = ""
    if command.reference_sections:
        reference_sections = "".join(
            f"\n\n{section.title}:\n{_reference_text(section.values)}"
            for section in command.reference_sections
        )
    common_modules = ""
    if command.common_modules:
        common_modules = "\n\nCommon --modules values:\n  " + ", ".join(
            command.common_modules
        )
    common_types = ""
    if command.common_types:
        common_types = "\n\nCommon --type values:\n  " + ", ".join(command.common_types)
    notes = ""
    if command.notes:
        notes = "\n\nNotes:\n" + "\n".join(f"  {note}" for note in command.notes)
    return (
        f"Yahoo endpoint:\n  {command.yahoo_url}\n\n"
        f"Examples:\n{_examples_text(command.examples)}"
        f"{reference_sections}"
        f"{field_reference}"
        f"{common_modules}"
        f"{common_types}"
        f"{notes}"
    )


def _add_global_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--version",
        action="version",
        version=f"Yogurt {__version__}",
        help="Show the program version and exit.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging to stderr.",
    )
    parser.add_argument(
        "--no-session-cache",
        action="store_true",
        help="Do not load or save Yahoo cookie/crumb session state.",
    )
    parser.add_argument(
        "--refresh-session",
        action="store_true",
        help="Ignore any cached Yahoo session and establish a fresh one.",
    )
    parser.add_argument(
        "--session-cache",
        type=Path,
        metavar="PATH",
        help="Override the Yahoo session cache path.",
    )


def _default_for_param(param: ParamSpec) -> object:
    if param.default in {"now", "now-3d"}:
        return argparse.SUPPRESS
    if param.default == "today":
        return datetime.now(timezone.utc).date().isoformat()
    if (
        param.allow_empty_default
        and isinstance(param.default, str)
        and len(param.default) == 0
    ):
        return argparse.SUPPRESS
    return param.default


def _dynamic_default_for_param(
    spec: ParamSpec, current_timestamp: int
) -> ParamValue | None:
    multiplier = 1000 if spec.kind is ParamKind.DATETIME_MILLISECONDS else 1
    if spec.default == "now":
        return current_timestamp * multiplier
    if spec.default == "now-3d":
        return (current_timestamp - _THREE_DAYS_SECONDS) * multiplier
    return None


def _add_command_param(parser: argparse.ArgumentParser, param: ParamSpec) -> None:
    if param.positional:
        parser.add_argument(
            param.name,
            metavar=param.metavar,
            help=param.help,
        )
        return
    parser.add_argument(
        param.option,
        dest=param.name,
        required=param.required,
        default=_default_for_param(param),
        metavar=param.metavar,
        help=param.help,
    )


def _set_command_parser(parser: argparse.ArgumentParser, command: CommandSpec) -> None:
    for param in command.params:
        _add_command_param(parser, param)
    parser.set_defaults(command_kind="modeled", command_name=command.name)


def build_parser() -> argparse.ArgumentParser:
    """Build Yogurt's adaptive argument parser.

    Returns:
        argparse.ArgumentParser: The configured root parser.
    """

    parser = argparse.ArgumentParser(
        prog="yogurt",
        description=(
            "Expose Yahoo Finance endpoints to the command line and print raw "
            "JSON response bodies."
        ),
        epilog="Run `yogurt <endpoint> --help` for endpoint-specific parameters.",
        formatter_class=_HelpFormatter,
        add_help=False,
    )
    _add_help_option(parser)
    _add_global_options(parser)
    subparsers = parser.add_subparsers(
        title="commands",
        metavar="COMMAND",
        dest="subcommand",
    )
    for command in COMMANDS:
        command_parser = subparsers.add_parser(
            command.name,
            help=command.summary,
            description=command.description,
            epilog=_epilog_for_command(command),
            formatter_class=_HelpFormatter,
            add_help=False,
        )
        _add_help_option(command_parser)
        _set_command_parser(command_parser, command)

    raw_parser = subparsers.add_parser(
        "raw",
        help="Custom Yahoo query path for data Yogurt does not model yet.",
        description=(
            "Pass through a query path and NAME=VALUE parameters for ad hoc Yahoo "
            "Finance requests."
        ),
        epilog=(
            "Example:\n"
            "  yogurt raw /v7/finance/quote --param symbols=AAPL,MSFT "
            "--param formatted=true"
        ),
        formatter_class=_HelpFormatter,
        add_help=False,
    )
    _add_help_option(raw_parser)
    raw_parser.add_argument("path", help="Yahoo query path, such as /v7/finance/quote.")
    raw_parser.add_argument(
        "--param",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="Query parameter to pass through. Repeat for multiple parameters.",
    )
    raw_parser.add_argument(
        "--no-crumb",
        action="store_true",
        help="Do not add Yahoo's crumb parameter to the request.",
    )
    raw_parser.set_defaults(command_kind="raw")
    return parser


def _configure_logging(*, verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s:%(message)s")


def _params_for_command(
    command: CommandSpec, namespace: argparse.Namespace
) -> dict[str, ParamValue]:
    params: dict[str, ParamValue] = {}
    date_pair = _date_pair_for_command(command)
    if date_pair is not None:
        start_spec, end_spec = date_pair
        explicit_start = hasattr(namespace, start_spec.name)
        explicit_end = hasattr(namespace, end_spec.name)
        if explicit_end and not explicit_start:
            message = (
                f"{end_spec.option} cannot be provided without {start_spec.option}"
            )
            raise ValueError(message)
    current_timestamp = int(time.time())
    for spec in command.params:
        if not hasattr(namespace, spec.name):
            dynamic_default = _dynamic_default_for_param(spec, current_timestamp)
            if dynamic_default is not None:
                params[spec.name] = dynamic_default
                continue
            if (
                spec.allow_empty_default
                and isinstance(spec.default, str)
                and len(spec.default) == 0
            ):
                params[spec.name] = ""
            continue
        value = getattr(namespace, spec.name)
        if value is None:
            continue
        if spec.path_param:
            continue
        if isinstance(value, bool | int | float):
            params[spec.name] = value
            continue
        params[spec.name] = coerce_param(spec, value)
    return params


def _date_pair_for_command(command: CommandSpec) -> tuple[ParamSpec, ParamSpec] | None:
    names = _DATE_PAIR_NAMES.get(command.name)
    if names is None:
        return None
    start = next(spec for spec in command.params if spec.name == names[0])
    end = next(spec for spec in command.params if spec.name == names[1])
    return start, end


def _validate_command_params(
    command: CommandSpec, params: dict[str, ParamValue]
) -> None:
    date_pair = _date_pair_for_command(command)
    if date_pair is not None:
        start_spec, end_spec = date_pair
        if start_spec.name in params and end_spec.name in params:
            start = params[start_spec.name]
            end = params[end_spec.name]
            if not isinstance(start, int) or not isinstance(end, int):
                message = (
                    f"{start_spec.option} and {end_spec.option} must be datetime values"
                )
                raise ValueError(message)
            if end <= start:
                message = f"{end_spec.option} must be greater than {start_spec.option}"
                raise ValueError(message)

    if command.name == "chart":
        interval = params.get("interval")
        allowed_intervals = {"1m", "5m", "15m", "1d", "1wk", "1mo"}
        if interval not in allowed_intervals:
            allowed_text = ", ".join(sorted(allowed_intervals))
            message = (
                f"--interval unsupported value {interval!r}; "
                f"expected one of: {allowed_text}"
            )
            raise ValueError(message)


def _path_for_command(command: CommandSpec, namespace: argparse.Namespace) -> str:
    path_values: dict[str, str] = {}
    for _, field_name, _, _ in Formatter().parse(command.path):
        if field_name is None:
            continue
        spec = next(param for param in command.params if param.name == field_name)
        raw_value = getattr(namespace, spec.name)
        coerced_value = coerce_param(spec, raw_value)
        path_values[field_name] = quote(str(coerced_value), safe="")
    return command.path.format(**path_values)


def _params_for_raw(raw_params: Sequence[str]) -> dict[str, ParamValue]:
    params: dict[str, ParamValue] = {}
    for raw_param in raw_params:
        name, separator, value = raw_param.partition("=")
        if not separator or not name:
            message = f"--param expects NAME=VALUE, got {raw_param!r}"
            raise ValueError(message)
        params[name] = value
    return params


async def _run_async(
    namespace: argparse.Namespace,
    stdout: TextIO,
    client: _YahooClientProtocol,
) -> int:
    try:
        if namespace.command_kind == "modeled":
            command = COMMANDS_BY_NAME[namespace.command_name]
            params = _params_for_command(command, namespace)
            _validate_command_params(command, params)
            body = await client.get(
                _path_for_command(command, namespace),
                params,
                use_crumb=command.use_crumb,
            )
        elif namespace.command_kind == "raw":
            body = await client.get(
                namespace.path,
                _params_for_raw(namespace.param),
                use_crumb=not namespace.no_crumb,
            )
        else:
            return 2
        stdout.write(body)
        if body and not body.endswith("\n"):
            stdout.write("\n")
        return 0
    finally:
        await client.aclose()


def main(
    argv: Sequence[str] | None = None,
    *,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    client: _YahooClientProtocol | None = None,
) -> int:
    """Run the Yogurt CLI.

    Returns:
        int: Process-style exit code.
    """

    parser = build_parser()
    output = stdout or sys.stdout
    if stdout is None:
        reconfigure = getattr(output, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    error_output = stderr or sys.stderr
    namespace = parser.parse_args(argv)
    if not hasattr(namespace, "command_kind"):
        parser.print_help(error_output)
        return 2

    _configure_logging(verbose=namespace.verbose)
    active_client = client or YahooClient(
        use_session_cache=not namespace.no_session_cache,
        refresh_session=namespace.refresh_session,
        session_cache_path=namespace.session_cache,
    )
    try:
        return asyncio.run(_run_async(namespace, output, active_client))
    except (ValueError, YogurtError) as exc:
        error_output.write(f"yogurt: error: {exc}\n")
        return 1
