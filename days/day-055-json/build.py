"""Day 055 build — a settings store: defaults, overrides, and a safe save.

    python3 build.py                # the demonstration
    python3 build.py my-config.json # load and validate a file of your own

THE SHAPE OF EVERY REAL CONFIGURATION SYSTEM:

    defaults (in code)  <-  a file  <-  environment  <-  command line
    least specific                                       most specific

Each layer overrides the one before it, and only the keys it mentions.
That last clause is the whole problem: a shallow dict update replaces
whole sections, so a user who sets one nested value silently loses the
other six.

THE DEFAULTS ARE ALSO THE SCHEMA. Every key that may exist is in
DEFAULTS, with a value of the type it must have — so an unknown key and a
wrong type are both detectable without writing a schema twice.

Everything is written to a temporary directory that is removed at the end.
"""

import difflib
import json
import os
import shutil
import sys
import tempfile
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

WIDTH = 78


# ###########################################################################
# THE DEFAULTS — every key that may exist, with the type it must have
# ###########################################################################

DEFAULTS = {
    "service": {
        "name": "unnamed",
        "host": "localhost",
        "port": 8080,
        "workers": 4,
    },
    "limits": {
        "rate_per_second": 100,
        "burst": 20,
        "timeout_seconds": 30.0,
        "max_body_mb": 10,
    },
    "logging": {
        "level": "INFO",
        "to_file": False,
        "path": "/var/log/app.log",
    },
    "features": {
        "beta_ui": False,
        "metrics": True,
        "tags": [],
    },
    "billing": {
        "currency": "GBP",
        "unit_price": Decimal("19.99"),      # NOT a float, deliberately
        "renews_on": date(2026, 4, 1),       # NOT a string, deliberately
    },
}

SECRET_KEYS = {"password", "token", "secret", "api_key"}


# ###########################################################################
# ENCODING THE TYPES JSON DOES NOT HAVE
# ###########################################################################

def encode(value):
    """Called only for values json cannot handle."""
    if isinstance(value, Decimal):
        return {"__type__": "decimal", "value": str(value)}
    if isinstance(value, datetime):
        return {"__type__": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"__type__": "date", "value": value.isoformat()}
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    raise TypeError(f"cannot serialise {type(value).__name__}: {value!r}")


def decode(obj):
    """object_hook: reverse the tags on the way back in."""
    kind = obj.get("__type__")
    if kind == "decimal":
        return Decimal(obj["value"])
    if kind == "datetime":
        return datetime.fromisoformat(obj["value"])
    if kind == "date":
        return date.fromisoformat(obj["value"])
    return obj


# ###########################################################################
# THE MERGE — the part everybody gets wrong the first time
# ###########################################################################

def shallow_merge(base, override):
    """What `{**base, **override}` and dict.update() do. WRONG here."""
    return {**base, **override}


def deep_merge(base, override):
    """Recursive, and it does not mutate either argument.

    A dict merges key by key; anything else REPLACES. That second rule is
    also a decision: a user who sets `tags` means "these tags", not "these
    as well as the defaults". Appending would make it impossible to
    express an empty list.
    """
    merged = dict(base)
    for key, value in override.items():
        if (key in merged and isinstance(merged[key], dict)
                and isinstance(value, dict)):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


# ###########################################################################
# VALIDATION, AGAINST THE DEFAULTS
# ###########################################################################

def validate(candidate, schema=DEFAULTS, path=""):
    """Return a list of problems. The DEFAULTS are the schema.

    Two things are checked, and both are cheap only because the defaults
    already describe the whole shape:

        unknown keys    a typo in a config file is otherwise silent
        wrong types     'port': '8080' is a string and breaks arithmetic
                        two hundred lines later
    """
    problems = []
    for key, value in candidate.items():
        here = f"{path}{key}"
        if key not in schema:
            near = difflib.get_close_matches(key, schema, n=1, cutoff=0.6)
            hint = f"; did you mean {near[0]!r}?" if near else ""
            problems.append(f"{here}: unknown setting{hint}")
            continue

        expected = schema[key]
        if isinstance(expected, dict):
            if not isinstance(value, dict):
                problems.append(f"{here}: expected a section, got "
                                f"{type(value).__name__}")
            else:
                problems += validate(value, expected, f"{here}.")
            continue

        # bool before int: isinstance(True, int) is True in Python
        if isinstance(expected, bool):
            if not isinstance(value, bool):
                problems.append(f"{here}: expected true/false, got {value!r}")
        elif isinstance(expected, (int, float, Decimal)):
            if isinstance(value, bool) or not isinstance(
                    value, (int, float, Decimal)):
                problems.append(f"{here}: expected a number, got {value!r}")
        elif not isinstance(value, type(expected)):
            problems.append(f"{here}: expected "
                            f"{type(expected).__name__}, got "
                            f"{type(value).__name__}")
    return problems


# ###########################################################################
# THE STORE
# ###########################################################################

class SettingsError(Exception):
    """Raised when a settings file cannot be used."""


def load(path, defaults=DEFAULTS):
    """defaults <- file. Returns (settings, problems). Never half-applies."""
    path = Path(path)
    if not path.exists():
        return dict(defaults), [f"{path.name} not found, using defaults"]

    try:
        with open(path, encoding="utf-8") as f:
            user = json.load(f, object_hook=decode)
    except json.JSONDecodeError as exc:
        # Day 52: translate, and keep the line number the parser gave us.
        raise SettingsError(
            f"{path.name} is not valid JSON: {exc.msg} "
            f"at line {exc.lineno}, column {exc.colno}"
        ) from exc

    if not isinstance(user, dict):
        raise SettingsError(
            f"{path.name} must contain an object, not a "
            f"{type(user).__name__}"
        )

    problems = validate(user)
    return deep_merge(defaults, user), problems


def save(settings, path):
    """Write atomically: a crash mid-write must not destroy the old file."""
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    try:
        with open(temporary, "w", encoding="utf-8") as f:
            json.dump(settings, f, default=encode, indent=2,
                      sort_keys=True, ensure_ascii=False, allow_nan=False)
            f.write("\n")
        os.replace(temporary, path)              # Day 53
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return path


def redacted(settings):
    """A view safe to print or log. Never print a config object raw."""
    out = {}
    for key, value in settings.items():
        if isinstance(value, dict):
            out[key] = redacted(value)
        elif any(secret in key.lower() for secret in SECRET_KEYS):
            out[key] = "***"
        else:
            out[key] = value
    return out


# ###########################################################################
# RUN IT
# ###########################################################################

WORK = Path(tempfile.mkdtemp(prefix="day055-"))

USER_CONFIG = {
    "service": {"name": "billing-api", "port": 443},
    "features": {"beta_ui": True, "tags": ["eu", "canary"]},
    "billing": {"unit_price": Decimal("24.50")},
}

config_path = WORK / "settings.json"
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(USER_CONFIG, f, default=encode, indent=2, sort_keys=True)

print("=" * WIDTH)
print(f"{'THE MERGE THAT EVERYBODY GETS WRONG FIRST':^{WIDTH}}")
print("=" * WIDTH)

shallow = shallow_merge(DEFAULTS, USER_CONFIG)
deep = deep_merge(DEFAULTS, USER_CONFIG)

mentioned = sum(len(v) if isinstance(v, dict) else 1
                for v in USER_CONFIG.values())
print(f"\n  The user's file mentions {mentioned} settings across "
      f"{len(USER_CONFIG)} sections.")
print(f"  DEFAULTS has {sum(len(v) for v in DEFAULTS.values())} settings "
      f"across {len(DEFAULTS)} sections.\n")

print(f"  {'SETTING':<28}{'DEFAULT':<14}{'SHALLOW':<14}{'DEEP':<14}")
print("  " + "-" * (WIDTH - 4))
for section, key in [("service", "name"), ("service", "port"),
                     ("service", "host"), ("service", "workers"),
                     ("features", "beta_ui"), ("features", "metrics"),
                     ("billing", "unit_price"), ("billing", "currency")]:
    default = DEFAULTS[section][key]
    got_shallow = shallow[section].get(key, "GONE")
    got_deep = deep[section].get(key, "GONE")
    flag = "  <-" if got_shallow == "GONE" else ""
    print(f"  {section + '.' + key:<28}{str(default):<14}"
          f"{str(got_shallow):<14}{str(got_deep):<14}{flag}")

lost = sum(1 for section in DEFAULTS for key in DEFAULTS[section]
           if key not in shallow.get(section, {}))
print("  " + "-" * (WIDTH - 4))
print(f"  settings destroyed by the shallow merge: {lost}")

print(f"""
  `{{**defaults, **user}}` replaced three whole SECTIONS with the fragments
  the user wrote. {lost} settings that the user never mentioned — including
  every default port, worker count and currency in those sections —
  vanished, and nothing raised.

  This is the single commonest configuration bug there is, and it does not
  show up in testing because the developer's config file usually mentions
  everything.""")


# ###########################################################################
# LOADING, AND WHAT VALIDATION CATCHES
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'LOADING A FILE WITH FOUR MISTAKES IN IT':^{WIDTH}}")
print("=" * WIDTH)

BROKEN = {
    "service": {"name": "api", "port": "8080", "hots": "example.com"},
    "limits": {"burst": 50, "timeout_seconds": "thirty"},
    "features": {"beta_ui": "yes"},
    "loging": {"level": "DEBUG"},
}

broken_path = WORK / "broken.json"
with open(broken_path, "w", encoding="utf-8") as f:
    json.dump(BROKEN, f, indent=2)

settings, problems = load(broken_path)
print()
for problem in problems:
    print(f"  {problem}")

print("""
  Four kinds of mistake, all of them found before the program starts:

    'port': '8080'        a STRING. port + 1 is a TypeError, and the
                          traceback would have pointed at the arithmetic.
    'timeout_seconds'     'thirty' — the same, in a place that only fails
                          when a request finally times out.
    'beta_ui': 'yes'      truthy, so the feature turns ON, and would have
                          stayed on if 'no' were written instead.
    'hots' and 'loging'   typos. Without an unknown-key check these are
                          SILENT: the setting simply has no effect, and
                          somebody spends an afternoon on it.

  THE SUGGESTION comes free from having the defaults to hand.""")


# ###########################################################################
# THE FULL LIFECYCLE
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'DEFAULTS -> FILE -> ENVIRONMENT -> ARGUMENTS':^{WIDTH}}")
print("=" * WIDTH)

os.environ["APP_SERVICE__WORKERS"] = "16"
os.environ["APP_LOGGING__LEVEL"] = "DEBUG"


def from_environment(prefix="APP_", schema=DEFAULTS):
    """APP_SERVICE__WORKERS=16 -> {'service': {'workers': 16}}.

    Environment values are ALWAYS strings, so each one is converted using
    the type of the default it is overriding — the schema doing a second
    job.
    """
    overrides = {}
    for name, raw in os.environ.items():
        if not name.startswith(prefix):
            continue
        section, _, key = name[len(prefix):].lower().partition("__")
        if section not in schema or key not in schema[section]:
            continue
        default = schema[section][key]
        if isinstance(default, bool):
            value = raw.strip().lower() in ("1", "true", "yes", "on")
        elif isinstance(default, int):
            value = int(raw)
        elif isinstance(default, float):
            value = float(raw)
        elif isinstance(default, Decimal):
            value = Decimal(raw)
        else:
            value = raw
        overrides.setdefault(section, {})[key] = value
    return overrides


ARGUMENTS = {"service": {"port": 9000}, "logging": {"to_file": True}}

layers = [
    ("defaults", DEFAULTS),
    ("settings.json", json.loads(config_path.read_text(encoding="utf-8"),
                                 object_hook=decode)),
    ("environment", from_environment()),
    ("command line", ARGUMENTS),
]

final = {}
print(f"\n  {'LAYER':<18}{'service.port':>14}{'workers':>10}"
      f"{'log level':>12}{'price':>10}")
print("  " + "-" * (WIDTH - 4))
for label, layer in layers:
    final = deep_merge(final, layer)
    print(f"  {label:<18}{str(final['service']['port']):>14}"
          f"{str(final['service']['workers']):>10}"
          f"{str(final['logging']['level']):>12}"
          f"{str(final['billing']['unit_price']):>10}")

print("""
  Each row overrides only what it mentions. The port was set three times
  and the last one wins; the price was set once, in the file, and survives
  two more layers untouched.""")


# ###########################################################################
# SAVING
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'SAVING':^{WIDTH}}")
print("=" * WIDTH)

saved_path = save(final, WORK / "effective.json")
reloaded = json.loads(saved_path.read_text(encoding="utf-8"),
                      object_hook=decode)

print(f"\n  wrote {saved_path.name}, {saved_path.stat().st_size} bytes")
print("  first lines:")
for line in saved_path.read_text(encoding="utf-8").splitlines()[:8]:
    print(f"    {line}")

# Save it again with no changes: the bytes must be identical.
save(final, WORK / "effective-again.json")
stable = (saved_path.read_bytes()
          == (WORK / "effective-again.json").read_bytes())

# A crash mid-save must leave the old file intact.
original = saved_path.read_bytes()


def exploding_encode(value):
    raise RuntimeError("disk went away")


try:
    with open(saved_path.with_suffix(".json.tmp"), "w", encoding="utf-8") as f:
        json.dump(final, f, default=exploding_encode)
    os.replace(saved_path.with_suffix(".json.tmp"), saved_path)
except (RuntimeError, TypeError):
    saved_path.with_suffix(".json.tmp").unlink(missing_ok=True)

survived = saved_path.read_bytes() == original

print(f"""
  {'sorted, so re-saving gives an empty diff':<52}{stable}
  {'a crash mid-save left the old file intact':<52}{survived}

  sort_keys=True is not cosmetic. Without it, dict order leaks into the
  file, a no-op save produces a diff, and a config file in git becomes
  unreviewable.""")

print("\n  redacted view (what is safe to log):")
with_secret = deep_merge(final, {"service": {"api_key": "sk-live-931"}})
print(f"    api_key in the object   "
      f"{with_secret['service']['api_key']!r}")
print(f"    api_key when printed    "
      f"{redacted(with_secret)['service']['api_key']!r}")


# ###########################################################################
# THE CHECKS
# ###########################################################################

print()
print("=" * WIDTH)
print(f"{'THE CHECKS':^{WIDTH}}")
print("=" * WIDTH)

bad_json = WORK / "bad.json"
bad_json.write_text('{"service": {"port": 8080,}}\n', encoding="utf-8")
try:
    load(bad_json)
    decode_message = ""
except SettingsError as exc:
    decode_message = str(exc)

not_object = WORK / "list.json"
not_object.write_text("[1, 2, 3]\n", encoding="utf-8")
try:
    load(not_object)
    list_refused = False
except SettingsError:
    list_refused = True

claims = [
    ("a deep merge keeps settings the user did not mention",
     deep["service"]["host"] == "localhost"),
    ("...where a shallow merge destroys them", lost == 5),
    ("an override the user DID write is applied",
     deep["service"]["port"] == 443),
    ("a Decimal survives the file round trip",
     isinstance(reloaded["billing"]["unit_price"], Decimal)
     and reloaded["billing"]["unit_price"] == Decimal("24.50")),
    ("...and a date does too",
     reloaded["billing"]["renews_on"] == date(2026, 4, 1)),
    ("unknown keys are reported, not ignored",
     any("unknown setting" in p for p in problems)),
    ("...with a suggestion", any("did you mean" in p for p in problems)),
    ("a string where a number belongs is caught",
     any("service.port" in p for p in problems)),
    ("'yes' is not accepted as a boolean",
     any("features.beta_ui" in p for p in problems)),
    ("environment values are converted using the default's type",
     final["service"]["workers"] == 16
     and isinstance(final["service"]["workers"], int)),
    ("later layers win", final["service"]["port"] == 9000),
    ("saving twice gives byte-identical output", stable),
    ("a crash mid-save leaves the old file intact", survived),
    ("invalid JSON is reported with a line and column",
     "line 1" in decode_message and "column" in decode_message),
    ("a file containing a list is refused", list_refused),
    ("secrets are redacted for printing",
     redacted(with_secret)["service"]["api_key"] == "***"),
]

print()
for label, passed in claims:
    print(f"  {'PASS' if passed else 'FAIL':<6}{label}")
print("-" * WIDTH)
print(f"  {sum(p for _, p in claims)} of {len(claims)} checks pass")

print(f"""
  THE SECOND CHECK IS THE WHOLE DAY. `{{**defaults, **user}}` looks correct,
  passes any test whose fixture mentions every key, and silently deletes
  {lost} settings the moment a real user writes a three-line config file.

  THE FOURTH AND FIFTH ARE THE REASON FOR THE __type__ TAGS. A price
  written as a JSON number comes back as a float, and 19.99 as a float is
  not 19.99. The tag costs twelve characters in the file and removes a
  class of rounding bug entirely.""")
print("=" * WIDTH)

if len(sys.argv) >= 2:
    print(f"\nvalidating {sys.argv[1]}:", file=sys.stderr)
    try:
        yours, yours_problems = load(sys.argv[1])
        for problem in yours_problems or ["no problems found"]:
            print(f"  {problem}", file=sys.stderr)
    except SettingsError as exc:
        print(f"  {exc}", file=sys.stderr)

shutil.rmtree(WORK, ignore_errors=True)
os.environ.pop("APP_SERVICE__WORKERS", None)
os.environ.pop("APP_LOGGING__LEVEL", None)


# ---------------------------------------------------------------------------
# Extend it
# ---------------------------------------------------------------------------
#
#   * Replace deep_merge with dict.update and run the checks. Two fail,
#     and the failure is the bug you would otherwise ship.
#
#   * Add a `--set service.port=9000` argument parser that produces the
#     same nested shape from a dotted path. Day 64 does this with argparse.
#
#   * Make validate() RAISE an ExceptionGroup of Day 52's ValidationError
#     instead of returning strings. The call site gets shorter and the
#     errors get field names.
#
#   * Add a "version" key and a migration: if the file says version 1,
#     rename a setting and write version 2 back. Every configuration
#     system needs this eventually, and adding it late is much harder.
#
#   * Store the file as TOML instead (tomllib reads it, 3.11+). Compare
#     what a human sees when they open it — and notice that Python cannot
#     write TOML without a third-party library, which is the trade.
