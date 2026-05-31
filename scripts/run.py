#!/usr/bin/env python3
"""
NutriBudget BD - Unified Entry Point
Run this file to access all project features from one place.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main menu for running different project modes."""
    while True:
        print("\n" + "="*60)
        print("NUTRIBUDGET BD - UNIFIED ENTRY POINT")
        print("="*60)
        print("\n[MAIN MODES]")
        print("  1 = Interactive Meal Planner (main.py)")
        print("  2 = Run All Tests")
        
        print("\n[INDIVIDUAL TESTS]")
        print("  3 = Test All Goals (test_all_goals.py)")
        print("  4 = Test Budget Modes (test_budget_modes.py)")
        print("  5 = Test Cost Optimization (test_cost_optimization.py)")
        
        print("\n[DEBUG UTILITIES]")
        print("  6 = Debug Optimizer Full")
        print("  7 = Debug Optimizer")
        print("  8 = Debug Rounding")
        print("  9 = Debug Variety")
        print("  10 = Debug Test")
        
        print("\n[UTILITIES]")
        print("  11 = View Generated Reports (output folder)")
        print("  0 = Exit")
        
        choice = input("\nSelect option (0-11): ").strip()
        
        try:
            if choice == "1":
                run_main()
            elif choice == "2":
                run_all_tests()
            elif choice == "3":
                run_script("test_all_goals.py")
            elif choice == "4":
                run_script("test_budget_modes.py")
            elif choice == "5":
                run_script("test_cost_optimization.py")
            elif choice == "6":
                run_script("debug_optimizer_full.py")
            elif choice == "7":
                run_script("debug_optimizer.py")
            elif choice == "8":
                run_script("debug_rounding.py")
            elif choice == "9":
                run_script("debug_variety.py")
            elif choice == "10":
                run_script("debug_test.py")
            elif choice == "11":
                open_output_folder()
            elif choice == "0":
                print("\nGoodbye!")
                sys.exit(0)
            else:
                print("Invalid option. Please try again.")
        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            continue
        except Exception as e:
            print(f"\nError: {e}")
            continue

def run_main():
    """Run the interactive meal planner."""
    print("\n" + "="*60)
    print("Starting Interactive Meal Planner...")
    print("="*60 + "\n")
    subprocess.run([sys.executable, "main.py"], cwd=Path(__file__).parent)

def run_script(script_name):
    """Run a Python script."""
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print("="*60 + "\n")
    subprocess.run([sys.executable, script_name], cwd=Path(__file__).parent)

def run_all_tests():
    """Run all test files."""
    test_files = [
        "test_all_goals.py",
        "test_budget_modes.py",
        "test_cost_optimization.py"
    ]
    
    print(f"\n{'='*60}")
    print("Running All Tests...")
    print("="*60 + "\n")
    
    for test_file in test_files:
        print(f"\n--- Running {test_file} ---")
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent,
            capture_output=False
        )
        if result.returncode != 0:
            print(f"⚠ {test_file} failed")
        else:
            print(f"✓ {test_file} passed")

def open_output_folder():
    """Open the output folder in file explorer."""
    output_path = Path(__file__).parent / "output"
    if not output_path.exists():
        print("Output folder not found. Run the planner first to generate reports.")
        return
    
    print(f"\nOpening output folder: {output_path}")
    import os
    import platform
    
    if platform.system() == "Windows":
        os.startfile(output_path)
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", output_path])
    else:  # Linux
        subprocess.run(["xdg-open", output_path])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutdown requested. Goodbye!")
        sys.exit(0)
