from __future__ import annotations

import ast
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]  # kryptos/
TARGET_DIRS = ["src", "tests", "scripts"]  # add scripts for tool scripts

DEF_OR_CLASS = re.compile(r"^(def |class )")
DECORATOR = re.compile(r"^@")
FUNC_NAME = re.compile(r"^def (\w+)\b")
TOP_LEVEL = re.compile(r"^(def |class |@)")


def normalize_decorators(lines: list[str]) -> list[str]:
    """Collapse decorator blocks so there is no blank line between the last
    decorator and the function/class it decorates (fixes E304)."""
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        if DECORATOR.match(lines[i]):
            block: list[str] = []
            # Collect contiguous decorators
            while i < n and DECORATOR.match(lines[i]):
                block.append(lines[i])
                i += 1
            # Skip any blank lines directly after decorators
            while i < n and lines[i].strip() == "":
                i += 1  # remove blank lines after decorators
            # Append the decorated line (def/class) if present
            if i < n:
                block.append(lines[i])
                i += 1
            out.extend(block)
        else:
            out.append(lines[i])
            i += 1
    return out


def ensure_two_before(lines: list[str]) -> list[str]:
    """Ensure EXACTLY two blank lines precede each top-level def/class (E302),
    except when it is the first non-blank content OR directly follows a decorator.
    """
    out: list[str] = []
    saw_non_blank = False
    for line in lines:
        if DEF_OR_CLASS.match(line):
            if not saw_non_blank:
                out.append(line)
                saw_non_blank = True
                continue
            # Remove trailing blanks before evaluating context
            while out and out[-1].strip() == "":
                out.pop()
            # Find previous non-blank line
            prev_idx = len(out) - 1
            prev_line = None
            while prev_idx >= 0:
                if out[prev_idx].strip() != "":
                    prev_line = out[prev_idx]
                    break
                prev_idx -= 1
            if prev_line and DECORATOR.match(prev_line):
                # Decorator immediately precedes: no blank lines inserted
                out.append(line)
            else:
                out.extend(["\n", "\n", line])
        else:
            if line.strip():
                saw_non_blank = True
            out.append(line)
    return out


def ensure_two_after_blocks(lines: list[str]) -> list[str]:
    """Ensure EXACTLY two blank lines after each top-level function/class body (E305)
    when there is any following content (comment, code, or another block)."""
    text = "".join(lines)
    try:
        tree = ast.parse(text)
        end_lines: list[int] = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                end_lineno = getattr(node, "end_lineno", None)
                if end_lineno is None:
                    max_lineno = node.lineno
                    for child in ast.walk(node):
                        if hasattr(child, "lineno"):
                            max_lineno = max(max_lineno, child.lineno)  # type: ignore[arg-type]
                    end_lines.append(max_lineno)
                else:
                    end_lines.append(end_lineno)
        end_lines = sorted(set(end_lines))
    except SyntaxError:
        return lines

    markers = {ln - 1 for ln in end_lines}
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        out.append(lines[i])
        if i in markers:
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            if j < n:  # there is content after this block
                # Remove trailing blanks just appended
                while out and out[-1].strip() == "":
                    out.pop()
                out.extend(["\n", "\n"])
                # Skip original blank sequence
                k = i + 1
                while k < n and lines[k].strip() == "":
                    k += 1
                i = k
                continue
        i += 1
    return out


def remove_duplicate_funcs(lines: list[str]) -> list[str]:
    """Remove duplicated top-level functions with identical names, keeping first occurrence."""
    seen: set[str] = set()
    out: list[str] = []
    skip = False
    current: str | None = None
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
            else:
                m2 = FUNC_NAME.match(line)
                if m2 and (current is None or m2.group(1) != current):
                    skip = False
            if skip:
                continue
        out.append(line)
    return out


def tidy_blank_runs(lines: list[str]) -> list[str]:
    """Compress any run of >2 blank lines to exactly 2; normalize whitespace-only lines."""
    out: list[str] = []
    blank_run = 0
    for line in lines:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 2:
                out.append("\n")
        else:
            blank_run = 0
            out.append(line)
    return out


def fix_file(path: pathlib.Path) -> None:
    orig = path.read_text(encoding="utf-8").splitlines(keepends=True)
    text = orig
    text = normalize_decorators(text)
    text = remove_duplicate_funcs(text)
    text = ensure_two_before(text)
    text = ensure_two_after_blocks(text)
    text = tidy_blank_runs(text)
    if text and not text[-1].endswith("\n"):
        text[-1] += "\n"
    if text != orig:
        path.write_text("".join(text), encoding="utf-8")
        print(f"Updated: {path.relative_to(ROOT)}")
    else:
        print(f"No change: {path.relative_to(ROOT)}")


def main() -> None:
    # Process target directories
    for d in TARGET_DIRS:
        base = ROOT / d
        if not base.is_dir():
            continue
        for py in base.rglob("*.py"):
            fix_file(py)
    # Also process root-level python files (like main.py)
    for py in ROOT.glob("*.py"):
        fix_file(py)


if __name__ == "__main__":
    main()
