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
    out: list[str] = []
    i = 0
    n = len(lines)
    while i < n:
        if DECORATOR.match(lines[i]):
            block: list[str] = []
            while i < n and DECORATOR.match(lines[i]):
                block.append(lines[i])
                i += 1
            while i < n and lines[i].strip() == "":
                i += 1
            if i < n:
                block.append(lines[i])
                i += 1
            out.extend(block)
        else:
            out.append(lines[i])
            i += 1
    return out


def ensure_two_before(lines: list[str]) -> list[str]:
    out: list[str] = []
    saw_non_blank = False
    for line in lines:
        if DEF_OR_CLASS.match(line):
            if not saw_non_blank:
                out.append(line)
                saw_non_blank = True
                continue
            while out and out[-1].strip() == "":
                out.pop()
            prev_idx = len(out) - 1
            prev_line = None
            while prev_idx >= 0:
                if out[prev_idx].strip() != "":
                    prev_line = out[prev_idx]
                    break
                prev_idx -= 1
            if prev_line and DECORATOR.match(prev_line):
                out.append(line)
            else:
                out.extend(["\n", "\n", line])
        else:
            if line.strip():
                saw_non_blank = True
            out.append(line)
    return out


def ensure_two_after_blocks(lines: list[str]) -> list[str]:
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
            if j < n:
                while out and out[-1].strip() == "":
                    out.pop()
                out.extend(["\n", "\n"])
                k = i + 1
                while k < n and lines[k].strip() == "":
                    k += 1
                i = k
                continue
        i += 1
    return out
