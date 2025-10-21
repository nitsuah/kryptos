from __future__ import annotations
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEF_OR_CLASS = re.compile(r"^(def |class )")
FUNC_NAME = re.compile(r"^def (\w+)\b")

TARGET_DIRS = ["src", "tests"]


def ensure_two_blank_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        if DEF_OR_CLASS.match(line):
            blanks = 0
            j = len(out) - 1
            while j >= 0 and out[j].strip() == "":
                blanks += 1
                j -= 1
            for _ in range(max(0, 2 - blanks)):
                out.append("\n")
        out.append(line)
    return out


def remove_duplicate_defs(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    skip = False
    current = None
    for line in lines:
        m = FUNC_NAME.match(line)
        if m:
            name = m.group(1)
            if name in seen:
                skip = True
                current = name
            else:
                seen.add(name)
        if skip:
            if DEF_OR_CLASS.match(line) and not FUNC_NAME.match(line):
                skip = False
            elif FUNC_NAME.match(line) and FUNC_NAME.match(line).group(1) != current:
                skip = False
            if skip:
                continue
        out.append(line)
    return out


def process(path: pathlib.Path) -> None:
    text = path.read_text(encoding="utf-8").splitlines(keepends=True)
    text = ensure_two_blank_lines(text)
    text = remove_duplicate_defs(text)
    if text and not text[-1].endswith("\n"):
        text[-1] += "\n"
    path.write_text("".join(text), encoding="utf-8")
    print(f"Fixed: {path.relative_to(ROOT)}")


def main() -> None:
    for d in TARGET_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for py in base.rglob("*.py"):
            process(py)


if __name__ == "__main__":
    main()
