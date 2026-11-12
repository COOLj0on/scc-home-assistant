"""Decode the Grandis 650 HK medius_val.xml payload."""

from __future__ import annotations

import math
import re


def _round_like_javascript(value: float) -> int:
    """Round using JavaScript Math.round semantics."""
    return math.floor(value + 0.5)


def parse_payload(payload: str) -> dict[str, float | int | None]:
    """Parse the hexadecimal data embedded in the controller XML response.

    Args:
        payload: XML response containing the controller's hexadecimal payload.

    Returns:
        Decoded values for the main probes, relays, pumps, energy registers,
        and Flex 1 probes and relays.

    Raises:
        ValueError: If the response does not contain a complete hexadecimal
            payload.
    """
    raw = re.sub(r"<[^>]*>", "", payload)
    raw = re.sub(r"\s+", "", raw)
    if not raw or re.fullmatch(r"[0-9a-fA-F]+", raw) is None:
        raise ValueError("The controller response is not a hexadecimal payload")

    cursor = 0

    def read_next(length: int) -> str:
        nonlocal cursor
        chunk = raw[cursor : cursor + length]
        if len(chunk) != length:
            raise ValueError("The controller response is truncated")
        cursor += length
        return chunk

    def read_value(factor: int = 1) -> float:
        value = int(read_next(4), 16)
        if value > 32767:
            value -= 65536
        return _round_like_javascript(value / factor * 10) / 10

    int(read_next(2), 16)  # Payload size
    read_next(8)  # Header

    data: dict[str, float | int | None] = {}

    def read_temperature() -> float | None:
        value = read_value(10)
        return None if value >= 250 else value

    for index in range(1, 11):
        data[f"S{index}"] = read_temperature()

    data["Str"] = read_value()
    read_next(24)

    for index in range(1, 8):
        data[f"R{index}"] = _round_like_javascript(read_value(2))
    data["R0"] = _round_like_javascript(read_value(2))

    for index in range(1, 4):
        data[f"HE{index}"] = read_value(100)

    read_next(16)
    data["Q1"] = int(read_next(4), 16) + int(read_next(4), 16)

    read_next(8)
    data["Q2"] = int(read_next(4), 16)

    read_next(44)

    for index in range(1, 5):
        data[f"F1S{index}"] = read_temperature()

    for index in range(1, 4):
        data[f"F1R{index}"] = _round_like_javascript(read_value(2))

    return data
