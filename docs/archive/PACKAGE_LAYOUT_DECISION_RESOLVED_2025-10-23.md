# Package Layout Decision (Resolved 2025-10-23)

This is the archived resolution of `ISSUES/PACKAGE_LAYOUT_DECISION.md`.

Outcome:
- We adopted Option 3 (single canonical `kryptos/` package) by migrating/ consolidating code under
`kryptos/` and removing duplicate shim modules. All imports now use `from kryptos...`.
- Shims and duplicate modules referenced in the original options have been deleted.
- CI and tests pass on the unified layout; no rollback required.

Deferred / Not Implemented:
- Codemod producing `from k4...` style imports (we standardized on `kryptos` instead).

Follow-ups:
- Continue pruning any stray references in legacy docs (handled via broader docs cleanup).
- No further action; this decision is closed.

Original content below for traceability.

---

```markdown
{original decision document retained in git history}
```
