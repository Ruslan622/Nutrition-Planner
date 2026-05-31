"""
Complete Pipeline Runner
Runs all tests and generates complete output in one command:
  - All nutrition goals (maintenance, loss, gain)
  - All budget modes (cheapest, balanced, premium)
  - Formatted PDF receipts
  - Comparison reports
"""

import subprocess
import sys
from pathlib import Path

# Add backend to path so tests can find modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

def run_test(test_file: str):
    """Run a test file and handle output."""
    test_path = Path(__file__).parent.parent / 'tests' / test_file
    
    if not test_path.exists():
        print(f"❌ {test_file} not found!")
        return False
    
    print(f"\n{'='*80}")
    print(f"Running: {test_file}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            cwd=Path(__file__).parent,
            capture_output=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False


def main():
    """Run the complete pipeline."""
    print("\n" + "="*80)
    print("NUTRITION PLANNER - COMPLETE PIPELINE")
    print("="*80)
    
    tests = [
        "test_all_goals.py",
        "test_budget_modes.py",
    ]
    
    results = {}
    for test in tests:
        results[test] = run_test(test)
    
    # Summary
    print("\n" + "="*80)
    print("PIPELINE COMPLETE - SUMMARY")
    print("="*80)
    
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test}")
    
    print("\n📍 Output files saved to: output/")
    print("="*80 + "\n")
    
    all_passed = all(results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
