"""Analysis tools for cryptanalysis results."""

# Import legacy functions from parent analysis.py
import sys
from pathlib import Path

# New Sprint 4.3 components
from .strategic_coverage import (
    CoverageTrend,
    SaturationAnalysis,
    StrategicCoverageAnalyzer,
)

# Add parent to path to import analysis.py
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

# Import from analysis.py (the file, not the package)
try:
    import importlib.util

    spec = importlib.util.spec_from_file_location("kryptos_analysis_legacy", parent_path / "analysis.py")
    if spec and spec.loader:
        legacy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(legacy_module)
        check_cribs = legacy_module.check_cribs
        frequency_analysis = legacy_module.frequency_analysis
except Exception:
    # Fallback if import fails
    def check_cribs(*args, **kwargs):
        raise NotImplementedError("check_cribs not available")

    def frequency_analysis(*args, **kwargs):
        raise NotImplementedError("frequency_analysis not available")


__all__ = [
    "check_cribs",
    "frequency_analysis",
    "StrategicCoverageAnalyzer",
    "CoverageTrend",
    "SaturationAnalysis",
]
