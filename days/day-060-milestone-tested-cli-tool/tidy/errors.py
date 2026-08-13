"""Every exception this package raises deliberately.

Day 52's shape: one base class so a caller can write ONE except clause,
data on the exception so nobody parses a message, and a hierarchy whose
levels are decisions a caller might make.

    TidyError                    everything of ours
      SourceError                we could not read the input at all
        UnreadableFileError
        UnknownFormatError
      RecordError                one record is unusable
        MissingFieldError
        BadValueError
      OutputError                we could not write the result
"""

from __future__ import annotations

from pathlib import Path


class TidyError(Exception):
    """Base for everything tidy raises on purpose.

        except TidyError:      -> our failures
        except Exception:      -> ours, plus every bug we have
    """


class SourceError(TidyError):
    """The input could not be read. Nothing about the records is known."""

    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"{path.name}: {reason}")


class UnreadableFileError(SourceError):
    """It exists and we could not open or decode it."""


class UnknownFormatError(SourceError):
    """We have no reader for this extension."""


class RecordError(TidyError, ValueError):
    """One record is unusable. ALSO a ValueError, so older callers work.

    Carries the source, the line and the field, because a message without
    a line number is not actionable in a forty-thousand-row export.
    """

    def __init__(self, source: str, line: int, field: str,
                 problem: str, value: object = None) -> None:
        self.source = source
        self.line = line
        self.field = field
        self.problem = problem
        self.value = value
        super().__init__(str(self))

    def __str__(self) -> str:
        return f"{self.source}:{self.line} {self.field}: {self.problem}"

    def as_dict(self) -> dict[str, object]:
        """The same failure as data — for the rejects file and for tests."""
        return {
            "source": self.source,
            "line": self.line,
            "field": self.field,
            "problem": self.problem,
            "value": "" if self.value is None else str(self.value),
        }


class MissingFieldError(RecordError):
    """A required field was absent or empty."""


class BadValueError(RecordError):
    """A field was present and unusable."""


class OutputError(TidyError):
    """The result could not be written. The input is untouched."""

    def __init__(self, path: Path, reason: str) -> None:
        self.path = path
        self.reason = reason
        super().__init__(f"cannot write {path}: {reason}")
