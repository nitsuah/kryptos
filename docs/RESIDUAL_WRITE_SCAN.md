# Residual Write Scan (2025-10-23)

Breadcrumb: Operations > Hygiene > Write Scan

Purpose: enumerate any remaining direct filesystem ascents or absolute path usages that may bypass centralized helpers
in `kryptos.paths`.

## Scan Summary

- Direct `Path.home()` calls: none found.
- Direct `/tmp` references: none found.
- Absolute Windows root (`C:\\` or similar) references: none found.
- Manual parent ascents (`parents[`):
  - `kryptos/paths.py` fallback search loop (acceptable: repository root discovery).
  - Removed fragile ascents in `spy/extractor.py` (replaced with `get_repo_root()`).
  - Removed ascent in `k4/report.py` (now uses `get_repo_root()`).

## Remaining Items for Review

- `paths.get_repo_root()` fallback `return here.parents[1]` could be annotated with a TODO to raise
if pyproject missing rather than silently guessing.
- Consider adding a guard test asserting no new `parents[\d+]` patterns outside `paths.py`.

## Recommended Follow-ups

1. Add test `test_no_manual_parents_ascent` scanning for `parents[` excluding `paths.py`. 2. Replace fallback in
`get_repo_root()` with explicit error if pyproject not found (opt-in stricter mode). 3. Introduce a helper
`get_reports_root()` mirroring `ensure_reports_dir()` for consistency.

## Conclusion

All previously identified manual ascents now use path helpers. No out-of-repo write vectors detected in current scan
scope.
