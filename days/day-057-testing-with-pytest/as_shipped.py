"""The four functions EXACTLY as Day 40 shipped them, bugs included.

This file is a museum piece. It exists so the tests can demonstrate the
failure and the fix side by side, on the same assertions — because a bug
report you cannot reproduce is an opinion.

Day 40's package has since been corrected (version 1.1.0). Nothing here
is imported by anything except the tests.
"""


def human_bytes(count):
    """Day 40 version. Rounds 1048575 up to '1024.0 KB'."""
    size = float(count)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def duration(seconds):
    """Day 40 version. duration(-5) is '-1:59:55'."""
    seconds = int(seconds)
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def slugify(text):
    """Day 40 version. Keeps non-ASCII letters, so the slug is not URL-safe."""
    kept = [ch.lower() if ch.isalnum() else " " for ch in text]
    return "-".join("".join(kept).split())


def dig(data, *keys, default=None):
    """Day 40 version. A stored None is indistinguishable from a missing key."""
    for key in keys:
        if isinstance(data, dict):
            if key not in data:
                return default
            data = data[key]
        elif isinstance(data, (list, tuple)):
            if not isinstance(key, int) or not -len(data) <= key < len(data):
                return default
            data = data[key]
        else:
            return default
    return default if data is None else data
