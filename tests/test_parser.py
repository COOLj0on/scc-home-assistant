"""Tests for the Grandis payload parser."""

from __future__ import annotations

import unittest
from pathlib import Path
from runpy import run_path

INTEGRATION_PATH = Path(__file__).parents[1] / "custom_components" / "scc"
parse_payload = run_path(str(INTEGRATION_PATH / "parser.py"))["parse_payload"]
CONSTANTS = run_path(str(INTEGRATION_PATH / "const.py"))
SENSOR_KEYS = CONSTANTS["SENSOR_KEYS"]
PERCENTAGE_SENSOR_KEYS = CONSTANTS["PERCENTAGE_SENSOR_KEYS"]


def _payload(
    temperatures: list[int],
    power: int,
    relays: list[int],
    pumps: list[int],
    q1: tuple[int, int],
    q2: int,
    flex_temperatures: list[int],
    flex_relays: list[int],
) -> str:
    """Build a payload using the offsets expected by the legacy flow."""
    raw = (
        "EE"
        + "00" * 4
        + "".join(f"{value & 0xFFFF:04X}" for value in temperatures)
        + f"{power & 0xFFFF:04X}"
        + "00" * 12
        + "".join(f"{value & 0xFFFF:04X}" for value in relays)
        + "".join(f"{value & 0xFFFF:04X}" for value in pumps)
        + "00" * 8
        + "".join(f"{value:04X}" for value in q1)
        + "00" * 4
        + f"{q2:04X}"
        + "00" * 22
        + "".join(f"{value & 0xFFFF:04X}" for value in flex_temperatures)
        + "".join(f"{value & 0xFFFF:04X}" for value in flex_relays)
    )
    return f"<data>{raw}</data>"


class ParsePayloadTests(unittest.TestCase):
    """Verify legacy decoding and malformed-response handling."""

    def test_decodes_all_sections_and_signed_values(self) -> None:
        payload = _payload(
            temperatures=[215, 120, 345, 180, 2500, 0, 305, 190, 225, 75],
            power=125,
            relays=[1, 2, 3, 4, 5, 6, 7, 8],
            pumps=[10, 20, 30],
            q1=(10, 11),
            q2=20,
            flex_temperatures=[300, 2500, 0xFFCE, 180],
            flex_relays=[2, 1, 0xFFFF],
        )

        data = parse_payload(payload)

        self.assertEqual(set(data), set(SENSOR_KEYS))
        self.assertEqual(len(data), 31)
        self.assertEqual(
            PERCENTAGE_SENSOR_KEYS,
            {"R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7", "HE1", "HE2", "HE3"},
        )
        self.assertEqual(data["S1"], 21.5)
        self.assertIsNone(data["S5"])
        self.assertEqual(data["R1"], 1)
        self.assertEqual(data["HE1"], 0.1)
        self.assertEqual(data["Q1"], 21)
        self.assertEqual(data["Q2"], 20)
        self.assertEqual(data["F1S1"], 30)
        self.assertIsNone(data["F1S2"])
        self.assertEqual(data["F1S3"], -5)
        self.assertEqual(data["F1R1"], 1)
        self.assertEqual(data["F1R3"], 0)

    def test_accepts_whitespace_in_xml_payload(self) -> None:
        payload = _payload(
            temperatures=[100] * 10,
            power=0,
            relays=[0] * 8,
            pumps=[0] * 3,
            q1=(0, 0),
            q2=0,
            flex_temperatures=[0] * 4,
            flex_relays=[0] * 3,
        )

        self.assertEqual(parse_payload(payload.replace("00", "00\n", 1))["S1"], 10)

    def test_rejects_truncated_or_non_hex_payloads(self) -> None:
        for payload in ("<data>EE00</data>", "<data>not-hex</data>"):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                parse_payload(payload)


if __name__ == "__main__":
    unittest.main()
