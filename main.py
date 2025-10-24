"""(Removed) This module was replaced by `kryptos.examples.sections_demo`.

Left intentionally minimal to avoid breaking entry points relying on
`python -m kryptos.main`; they should migrate to the example script or future
CLI subcommands.
"""

from __future__ import annotations


def main() -> None:  # pragma: no cover
    raise SystemExit("main.py moved: run `python -m kryptos.examples.sections_demo` or use the upcoming CLI.")


if __name__ == "__main__":  # pragma: no cover
    main()
