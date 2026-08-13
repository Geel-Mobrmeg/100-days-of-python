"""The command line: exit codes, the dry run, and the output stream."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from tidy import cli


def run(argv, sources=None):
    """Call main() with a captured stream. No capsys, no subprocess."""
    out = io.StringIO()
    code = cli.main([*(argv if isinstance(argv, list) else [argv])], out=out)
    return code, out.getvalue()


# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------

def test_a_source_is_required():
    code, text = run([])
    assert code == 2
    assert "required" in text


def test_help_prints_usage_and_exits_two():
    code, text = run(["--help"])
    assert code == 2
    assert "exit codes" in text


def test_an_unknown_option_is_refused(sources):
    code, text = run([str(sources), "--turbo"])
    assert code == 2
    assert "--turbo" in text


def test_a_missing_source_is_refused(tmp_path):
    code, text = run([str(tmp_path / "nope")])
    assert code == 2
    assert "does not exist" in text


def test_two_sources_are_refused(sources):
    code, text = run([str(sources), str(sources)])
    assert code == 2
    assert "only one source" in text


def test_out_needs_a_value(sources):
    code, text = run([str(sources), "-o"])
    assert code == 2


@pytest.mark.parametrize("flags, expected", [
    ([], {"write": False, "recursive": False, "quiet": False}),
    (["--write"], {"write": True, "recursive": False, "quiet": False}),
    (["-r"], {"write": False, "recursive": True, "quiet": False}),
    (["-q", "--write", "-r"], {"write": True, "recursive": True,
                               "quiet": True}),
])
def test_flags_are_parsed(sources, flags, expected):
    options = cli.parse_args([str(sources), *flags])
    assert options.write == expected["write"]
    assert options.recursive == expected["recursive"]
    assert options.quiet == expected["quiet"]


def test_out_defaults_and_overrides(sources):
    assert cli.parse_args([str(sources)]).out == Path("tidy-output")
    assert cli.parse_args([str(sources), "-o", "x"]).out == Path("x")
    assert cli.parse_args([str(sources), "--out", "y"]).out == Path("y")


# ---------------------------------------------------------------------------
# Running
# ---------------------------------------------------------------------------

def test_a_clean_run_exits_zero(sources):
    code, text = run([str(sources)])
    assert code == 0
    assert "3 file(s)" in text


def test_a_run_with_rejections_exits_one(sources):
    (sources / "bad.csv").write_text(
        "sku,region,sold_on,units,unit_price\nNOPE,north,2026-03-01,1,1\n",
        encoding="utf-8")
    code, text = run([str(sources)])
    assert code == 1
    assert "1 rejected" in text


def test_an_unreadable_file_exits_one_and_says_which(sources):
    (sources / "broken.json").write_text("{oops", encoding="utf-8")
    code, text = run([str(sources)])
    assert code == 1
    assert "UNREADABLE broken.json" in text


# ---------------------------------------------------------------------------
# The dry run
# ---------------------------------------------------------------------------

def test_the_dry_run_writes_nothing(sources, tmp_path):
    destination = tmp_path / "out"
    code, text = run([str(sources), "-o", str(destination)])
    assert code == 0
    assert "would write" in text
    assert "dry run" in text
    assert not destination.exists()


def test_write_creates_the_files(sources, tmp_path):
    destination = tmp_path / "out"
    code, text = run([str(sources), "-o", str(destination), "--write"])
    assert code == 0
    assert "wrote" in text
    assert sorted(p.name for p in destination.iterdir()) == [
        "clean.csv", "rejects.csv", "summary.csv", "summary.json"]


def test_the_dry_run_names_exactly_what_write_creates(sources, tmp_path):
    preview = run([str(sources), "-o", str(tmp_path / "out")])[1]
    real = run([str(sources), "-o", str(tmp_path / "out"), "--write"])[1]
    promised = {line.split()[2] for line in preview.splitlines()
                if line.startswith("would write")}
    delivered = {line.split()[1] for line in real.splitlines()
                 if line.startswith("wrote")}
    assert promised == delivered


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def test_quiet_prints_only_the_summary_line(sources):
    _, loud = run([str(sources)])
    _, quiet = run([str(sources), "-q"])
    assert "REGION" in loud
    assert "REGION" not in quiet
    assert "3 file(s)" in quiet


def test_a_long_rejection_list_is_truncated_with_a_count(sources):
    rows = "\n".join(f"NOPE-{n},north,2026-03-01,1,1" for n in range(15))
    (sources / "bad.csv").write_text(
        f"sku,region,sold_on,units,unit_price\n{rows}\n", encoding="utf-8")
    _, text = run([str(sources)])
    assert "15 rejected" in text
    assert "... 5 more" in text


def test_recursive_finds_a_nested_file(sources):
    nested = sources / "deep"
    nested.mkdir()
    (nested / "west.csv").write_text(
        "sku,region,sold_on,units,unit_price\nWID-001,west,2026-03-01,1,1.00\n",
        encoding="utf-8")
    assert "3 file(s)" in run([str(sources)])[1]
    assert "4 file(s)" in run([str(sources), "-r"])[1]


def test_a_single_file_works_as_a_source(sources):
    code, text = run([str(sources / "north.csv")])
    assert code == 0
    assert "1 file(s)" in text


def test_a_source_we_cannot_read_is_reported_not_crashed(tmp_path):
    unsupported = tmp_path / "book.xlsx"
    unsupported.write_text("not really a spreadsheet", encoding="utf-8")
    code, text = run([str(unsupported)])
    assert code == 2
    assert "no reader" in text


def test_a_write_failure_is_reported_and_exits_two(sources, tmp_path):
    """The `except TidyError` at the top of main(), exercised."""
    destination = tmp_path / "out"
    destination.mkdir()
    (destination / "summary.csv.tmp").mkdir()
    code, text = run([str(sources), "-o", str(destination), "--write"])
    assert code == 2
    assert "error: cannot write" in text


def test_the_installed_command_runs(sources):
    """END TO END, as a real process — the one thing nothing else proves.

    Every other test in this file calls main() directly. This one runs
    `python3 -m tidy`, which is what a user types, and checks the exit
    code the shell would see.
    """
    import subprocess
    import sys
    from pathlib import Path

    finished = subprocess.run(
        [sys.executable, "-m", "tidy", str(sources)],
        capture_output=True, text=True,
        cwd=Path(__file__).resolve().parents[1],
    )
    assert finished.returncode == 0
    assert "3 file(s)" in finished.stdout
    assert finished.stderr == ""
