"""Fixtures for the whole suite (Day 58).

Nothing here touches the network, the clock or a path outside tmp_path.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

GOOD_CSV = (
    "SKU,Region, Sold On ,Units,Unit Price\n"
    "WID-001,north,2026-03-01,12,4.50\n"
    "GZM-002,NORTH,2026-03-02,3,£12.00\n"
    "DHK-003,south,2026-03-02,40,2.25\n"
)


@pytest.fixture
def raw_record():
    """A factory (Day 58): each test states only what it cares about."""
    def build(**overrides):
        defaults = {
            "sku": "WID-001",
            "region": "north",
            "sold_on": "2026-03-01",
            "units": "12",
            "unit_price": "4.50",
        }
        return {**defaults, **overrides}
    return build


@pytest.fixture
def stream():
    """Text in, file-like out — no temporary files for reader tests."""
    return io.StringIO


@pytest.fixture
def sources(tmp_path):
    """A directory of three real files, one of each format."""
    (tmp_path / "north.csv").write_text(GOOD_CSV, encoding="utf-8")
    (tmp_path / "south.json").write_text(json.dumps([
        {"sku": "SPR-006", "region": "south", "sold_on": "2026-03-01",
         "units": 5, "unit_price": "48.00"},
    ]), encoding="utf-8")
    (tmp_path / "east.jsonl").write_text(
        '{"sku": "BLT-015", "region": "east", "sold_on": "2026-03-01", '
        '"units": 60, "unit_price": "2.00"}\n', encoding="utf-8")
    (tmp_path / "notes.md").write_text("not data\n", encoding="utf-8")
    return tmp_path
