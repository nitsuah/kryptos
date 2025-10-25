#!/usr/bin/env python3
"""Test provenance tracking functionality."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add src to path for local testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from kryptos.paths import get_provenance_info  # noqa: E402


def test_provenance_basic():
    """Test basic provenance info capture."""
    print("Testing basic provenance capture...")
    info = get_provenance_info()

    print("\nProvenance Information:")
    print(json.dumps(info, indent=2))

    # Verify expected keys
    required_keys = [
        "timestamp",
        "python_version",
        "python_version_info",
        "platform",
        "repo_root",
        "git_commit",
        "git_branch",
        "git_dirty",
    ]

    missing = [k for k in required_keys if k not in info]
    if missing:
        print(f"\n❌ Missing keys: {missing}")
        return False

    print("\n✓ All required keys present")

    # Verify git info (should be available in repo)
    if info["git_commit"]:
        print(f"✓ Git commit: {info['git_commit'][:8]}...")
    else:
        print("⚠ Git commit not available")

    if info["git_branch"]:
        print(f"✓ Git branch: {info['git_branch']}")
    else:
        print("⚠ Git branch not available")

    if info["git_dirty"] is not None:
        status = "dirty" if info["git_dirty"] else "clean"
        print(f"✓ Git status: {status}")
    else:
        print("⚠ Git status not available")

    return True


def test_provenance_with_params():
    """Test provenance with custom parameters."""
    print("\n" + "=" * 80)
    print("Testing provenance with custom parameters...")

    params = {
        "hypothesis": "TranspositionThenHill",
        "transposition_candidates": 20,
        "hill_limit": 1000,
        "seed": 42,
    }

    info = get_provenance_info(include_params=params)

    print("\nProvenance with Parameters:")
    print(json.dumps(info, indent=2))

    if "params" in info and info["params"] == params:
        print("\n✓ Custom parameters included correctly")
        return True
    else:
        print("\n❌ Custom parameters not included correctly")
        return False


def test_provenance_serialization():
    """Test that provenance info can be serialized to JSON."""
    print("\n" + "=" * 80)
    print("Testing JSON serialization...")

    info = get_provenance_info(include_params={"test": "value"})

    try:
        json_str = json.dumps(info, indent=2)
        parsed = json.loads(json_str)
        print(f"\n✓ Successfully serialized {len(json_str)} bytes")
        print(f"✓ Successfully deserialized {len(parsed)} keys")
        return True
    except Exception as e:
        print(f"\n❌ Serialization failed: {e}")
        return False


if __name__ == "__main__":
    results = []

    results.append(test_provenance_basic())
    results.append(test_provenance_with_params())
    results.append(test_provenance_serialization())

    print("\n" + "=" * 80)
    print("Summary:")
    print(f"  Passed: {sum(results)}/{len(results)}")

    if all(results):
        print("\n✓ All tests passed!")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)
