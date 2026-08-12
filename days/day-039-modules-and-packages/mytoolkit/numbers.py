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
    >>> human_bytes(1024 * 1024 - 1)
    '1.0 MB'
    """
    size = float(count)
    units = ("B", "KB", "MB", "GB", "TB")
    index = 0
    while index < len(units) - 1:
        # Compare the value AS IT WILL BE SHOWN. 1048575 bytes is
        # 1023.99902 KB, which formats as '1024.0 KB' — a quantity that
        # does not exist. Rounding before the comparison promotes it.
        shown = abs(size) if index == 0 else round(abs(size), 1)
        if shown < 1024:
            break
        size /= 1024
        index += 1
    if units[index] == "B":
        return f"{int(size)} {units[index]}"
    return f"{size:.1f} {units[index]}"


def duration(seconds):
    """Return a number of seconds as h:mm:ss or m:ss.

    >>> duration(75)
    '1:15'
    >>> duration(3725)
    '1:02:05'
    >>> duration(0)
    '0:00'
    >>> duration(-75)
    '-1:15'
    """
    seconds = int(seconds)
    # divmod on a negative number floors, so divmod(-5, 3600) is
    # (-1, 3595) and the naive version prints '-1:59:55'. Take the sign
    # off first and put it back on the front.
    sign = "-" if seconds < 0 else ""
    hours, rest = divmod(abs(seconds), 3600)
    minutes, secs = divmod(rest, 60)
    if hours:
        return f"{sign}{hours}:{minutes:02d}:{secs:02d}"
    return f"{sign}{minutes}:{secs:02d}"
