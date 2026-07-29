"""Numeric helpers."""

__all__ = ["clamp", "percent", "human_bytes", "duration"]


def clamp(value, low, high):
    """Return value limited to the range low..high.

    >>> clamp(15, 0, 10)
    10
    >>> clamp(-3, 0, 10)
    0
    >>> clamp(5, 0, 10)
    5
    """
    if low > high:
        raise ValueError(f"low ({low}) is above high ({high})")
    return max(low, min(value, high))


def percent(part, whole, places=1):
    """Return part of whole as a percentage string, safe when whole is 0.

    >>> percent(1, 4)
    '25.0%'
    >>> percent(1, 3, places=2)
    '33.33%'
    >>> percent(5, 0)
    'n/a'
    """
    if not whole:
        return "n/a"
    return f"{part / whole:.{places}%}"


def human_bytes(count):
    """Return a byte count as a human-readable string.

    >>> human_bytes(512)
    '512 B'
    >>> human_bytes(2048)
    '2.0 KB'
    >>> human_bytes(1_500_000_000)
    '1.4 GB'
    """
    size = float(count)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def duration(seconds):
    """Return a number of seconds as h:mm:ss or m:ss.

    >>> duration(75)
    '1:15'
    >>> duration(3725)
    '1:02:05'
    >>> duration(0)
    '0:00'
    """
    seconds = int(seconds)
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"
