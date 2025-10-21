from __future__ import annotations
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]  # kryptos root

TARGETS = [
    "src/scoring/fitness.py",
    "src/stages/interface.py",
    "src/stages/mock_stage.py",
    "tests/test_scoring_fallback.py",
    "tests/test_stage_interface.py",
    "tests/test_ciphers_polybius_abc.py",
]

DEF_OR_CLASS = re.compile(r"^(def |class )")


def ensure_two_blank_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        if DEF_OR_CLASS.match(line):
            # count existing blank lines
            blanks = 0
            j = len(out) - 1
            while j >= 0 and out[j].strip() == "":
                blanks += 1
                j -= 1
            for _ in range(max(0, 2 - blanks)):
                out.append("\n")
        out.append(line)
    return out


def dedupe_function(lines: list[str], name: str) -> list[str]:
    pattern = re.compile(rf"^def {name}\b")
    seen = False
    out: list[str] = []
    skipping = False
    for line in lines:
        if pattern.match(line):
            if seen:
                skipping = True
            else:
                seen = True
        if skipping:
            if DEF_OR_CLASS.match(line) and not pattern.match(line):
                skipping = False
            continue
        out.append(line)
    return out


def process(path: pathlib.Path) -> None:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    lines = ensure_two_blank_lines(lines)
    if path.name == "test_scoring_fallback.py":
        lines = dedupe_function(lines, "score_candidate")
    if lines and not lines[-1].endswith("\n"):
        lines[-1] = lines[-1] + "\n"
    path.write_text("".join(lines), encoding="utf-8")
    print(f"Fixed: {path.relative_to(ROOT)}")


def main() -> None:
    for rel in TARGETS:
        p = ROOT / rel
        if p.is_file():
            process(p)
        else:
            print(f"Missing (skip): {rel}")


if __name__ == "__main__":
    main()
