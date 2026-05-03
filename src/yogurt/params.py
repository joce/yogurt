"""Endpoint parameter metadata and coercion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from yogurt.types import ParamValue


class ParamKind(str, Enum):
    """Supported CLI parameter kinds."""

    STRING = "string"
    CSV = "csv"
    INTEGER = "integer"
    DATETIME = "datetime"
    BOOLEAN = "boolean"


@dataclass(frozen=True, slots=True)
class ParamSpec:
    """Describe one endpoint query parameter."""

    name: str
    cli_name: str
    kind: ParamKind
    help: str
    positional: bool = False
    path_param: bool = False
    required: bool = False
    default: ParamValue | None = None
    metavar: str | None = None
    min_items: int | None = None
    max_items: int | None = None

    @property
    def option(self) -> str:
        """Return this parameter's long CLI option."""

        if self.positional:
            return self.name
        return f"--{self.cli_name}"


_TRUE_VALUES: Final[frozenset[str]] = frozenset({"1", "true", "t", "yes", "y", "on"})
_FALSE_VALUES: Final[frozenset[str]] = frozenset({"0", "false", "f", "no", "n", "off"})


def _coerce_csv_param(spec: ParamSpec, value: str) -> str:
    stripped = value.strip()
    if not stripped:
        message = f"{spec.option} cannot be empty"
        raise ValueError(message)
    items = [item.strip() for item in stripped.split(",")]
    if any(not item for item in items):
        message = f"{spec.option} cannot contain empty comma-separated values"
        raise ValueError(message)
    if spec.min_items is not None and len(items) < spec.min_items:
        message = (
            f"{spec.option} expects at least {spec.min_items} "
            f"comma-separated value; got {len(items)}"
        )
        raise ValueError(message)
    if spec.max_items is not None and len(items) > spec.max_items:
        message = (
            f"{spec.option} accepts at most {spec.max_items} "
            f"comma-separated values; got {len(items)}"
        )
        raise ValueError(message)
    return ",".join(items)


def parse_boolean(value: str) -> bool:
    """Parse a CLI boolean value.

    Returns:
        bool: Parsed boolean.

    Raises:
        ValueError: If the value is not a recognized boolean spelling.
    """

    normalized = value.strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    message = f"expected boolean value, got {value!r}"
    raise ValueError(message)


def parse_datetime(value: str) -> int:
    """Parse a Unix timestamp or datetime value for Yahoo query params.

    Returns:
        int: Unix timestamp in seconds.

    Raises:
        ValueError: If the value is not an integer timestamp, YYYY-MM-DD date, or
            ISO datetime.
    """

    stripped = value.strip()
    try:
        return int(stripped)
    except ValueError:
        pass

    try:
        parsed = datetime.fromisoformat(stripped.replace("Z", "+00:00"))
    except ValueError as exc:
        message = (
            f"expected Unix timestamp, YYYY-MM-DD date, or ISO datetime; got {value!r}"
        )
        raise ValueError(message) from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    else:
        parsed = parsed.astimezone(timezone.utc)
    return int(parsed.timestamp())


def coerce_param(spec: ParamSpec, value: str) -> ParamValue:
    """Coerce one CLI parameter value according to its endpoint spec.

    Returns:
        ParamValue: Coerced scalar query value.

    Raises:
        ValueError: If the value does not satisfy the parameter spec.
    """

    if spec.kind is ParamKind.STRING:
        stripped = value.strip()
        if not stripped:
            message = f"{spec.option} cannot be empty"
            raise ValueError(message)
        return stripped
    if spec.kind is ParamKind.CSV:
        return _coerce_csv_param(spec, value)
    if spec.kind is ParamKind.INTEGER:
        try:
            return int(value)
        except ValueError as exc:
            message = f"{spec.option} expects an integer"
            raise ValueError(message) from exc
    if spec.kind is ParamKind.DATETIME:
        try:
            return parse_datetime(value)
        except ValueError as exc:
            message = f"{spec.option} {exc}"
            raise ValueError(message) from exc
    if spec.kind is ParamKind.BOOLEAN:
        return parse_boolean(value)

    message = f"unsupported parameter kind: {spec.kind}"
    raise ValueError(message)
