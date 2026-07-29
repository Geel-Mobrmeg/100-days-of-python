"""Makes the package runnable:  python3 -m mytoolkit

__main__.py is what Python executes when a PACKAGE is run with -m. It is the
package-level equivalent of `if __name__ == "__main__":` in a single file,
and it is how tools like `python3 -m pytest` and `python3 -m http.server`
work.

Note that this module is not imported by __init__.py, so none of this code
runs when somebody does `from mytoolkit import slugify`. Library and command
stay separate.
"""

import sys

from . import __version__, containers, decorators, numbers, text

WIDTH = 70


def main(argv=None):
    """Print what the package contains. Returns an exit code."""
    argv = sys.argv[1:] if argv is None else argv

    print("=" * WIDTH)
    print(f"mytoolkit {__version__}")
    print("=" * WIDTH)

    modules = [
        ("numbers", numbers, "arithmetic and formatting"),
        ("text", text, "strings, slugs, initials"),
        ("containers", containers, "lists, dicts, nested data"),
        ("decorators", decorators, "timing, retry, cache, validation"),
    ]

    for name, module, description in modules:
        exported = [n for n in module.__all__]
        print(f"\n  {name:<14}{description}")
        for function_name in exported:
            function = getattr(module, function_name)
            summary = (function.__doc__ or "").strip().splitlines()[0]
            print(f"      {function_name:<14}{summary[:44]}")

    total = sum(len(m.__all__) for _, m, _ in modules)
    print()
    print("-" * WIDTH)
    print(f"  {total} public names across {len(modules)} submodules")
    print(f"  all of them importable as:  from mytoolkit import <name>")
    print("=" * WIDTH)

    if argv:
        print(f"\n(ignored arguments: {argv} — Day 63 adds a real CLI)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
