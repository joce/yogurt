"""Command-line interface for Yogurt."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from string import Formatter
from typing import TYPE_CHECKING, Protocol, TextIO
from urllib.parse import quote

from typing_extensions import override

from yogurt import __version__
from yogurt.client import YahooClient
from yogurt.endpoints import ENDPOINTS, ENDPOINTS_BY_NAME, EndpointSpec
from yogurt.exceptions import YogurtError
from yogurt.params import ParamSpec, coerce_param

if TYPE_CHECKING:
    from collections.abc import Sequence

    from yogurt.types import ParamValue


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

        super().__init__(prog, max_help_position=32, width=100)

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


def _examples_text(examples: tuple[str, ...]) -> str:
    return "\n".join(f"  {example}" for example in examples)


def _epilog_for_endpoint(endpoint: EndpointSpec) -> str:
    crumb = "yes" if endpoint.use_crumb else "no"
    common_fields = ""
    if endpoint.common_fields:
        common_fields = "\n\nCommon --fields values:\n  " + ", ".join(
            endpoint.common_fields
        )
    common_modules = ""
    if endpoint.common_modules:
        common_modules = "\n\nCommon --modules values:\n  " + ", ".join(
            endpoint.common_modules
        )
    notes = ""
    if endpoint.notes:
        notes = "\n\nNotes:\n" + "\n".join(f"  {note}" for note in endpoint.notes)
    return (
        f"Yahoo endpoint:\n  {endpoint.yahoo_url}\n\n"
        f"Uses Yahoo crumb/session:\n  {crumb}\n\n"
        "Output:\n"
        "  Writes Yahoo's raw response body to stdout without formatting or "
        "response mapping.\n\n"
        f"Examples:\n{_examples_text(endpoint.examples)}"
        f"{common_fields}"
        f"{common_modules}"
        f"{notes}"
    )


def _add_global_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
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


def _add_endpoint_param(parser: argparse.ArgumentParser, param: ParamSpec) -> None:
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
        default=param.default,
        metavar=param.metavar,
        help=param.help,
    )


def _set_endpoint_command(
    parser: argparse.ArgumentParser, endpoint: EndpointSpec
) -> None:
    for param in endpoint.params:
        _add_endpoint_param(parser, param)
    parser.set_defaults(command="endpoint", endpoint_name=endpoint.name)


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
    )
    _add_global_options(parser)
    subparsers = parser.add_subparsers(
        title="endpoints",
        metavar="ENDPOINT",
        dest="subcommand",
    )
    for endpoint in ENDPOINTS:
        endpoint_parser = subparsers.add_parser(
            endpoint.name,
            help=endpoint.summary,
            description=endpoint.description,
            epilog=_epilog_for_endpoint(endpoint),
            formatter_class=_HelpFormatter,
        )
        _set_endpoint_command(endpoint_parser, endpoint)

    raw_parser = subparsers.add_parser(
        "raw",
        help="Call a Yahoo query1.finance.yahoo.com path not yet modeled by Yogurt.",
        description=(
            "Call a Yahoo Finance query endpoint by path and write the raw response "
            "body to stdout."
        ),
        epilog=(
            "Example:\n"
            "  yogurt raw /v7/finance/quote --param symbols=AAPL,MSFT "
            "--param formatted=true"
        ),
        formatter_class=_HelpFormatter,
    )
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
    raw_parser.set_defaults(command="raw")
    return parser


def _configure_logging(*, verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(level=level, format="%(levelname)s:%(name)s:%(message)s")


def _params_for_endpoint(
    endpoint: EndpointSpec, namespace: argparse.Namespace
) -> dict[str, ParamValue]:
    params: dict[str, ParamValue] = {}
    for spec in endpoint.params:
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


def _path_for_endpoint(endpoint: EndpointSpec, namespace: argparse.Namespace) -> str:
    path_values: dict[str, str] = {}
    for _, field_name, _, _ in Formatter().parse(endpoint.path):
        if field_name is None:
            continue
        spec = next(param for param in endpoint.params if param.name == field_name)
        raw_value = getattr(namespace, spec.name)
        coerced_value = coerce_param(spec, raw_value)
        path_values[field_name] = quote(str(coerced_value), safe="")
    return endpoint.path.format(**path_values)


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
        if namespace.command == "endpoint":
            endpoint = ENDPOINTS_BY_NAME[namespace.endpoint_name]
            body = await client.get(
                _path_for_endpoint(endpoint, namespace),
                _params_for_endpoint(endpoint, namespace),
                use_crumb=endpoint.use_crumb,
            )
        elif namespace.command == "raw":
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
    if not hasattr(namespace, "command"):
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
