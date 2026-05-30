"""
Test script for the nutrition engine.
Simulates user input to test the MVP workflow.
"""

import sys
from io import StringIO
from core.calculator import NutritionCalculator
from core.planner import MealPlanner
from plans.report import MealPlanReport


def test_mvp():
    """Test the complete MVP workflow."""
    
    # Simulate user profile
    user = {
        "age": 28,
        "weight_kg": 75,
        "height_cm": 180,
        "sex": "M",
        "activity_level": 3,
        "goal": "maintenance",
    }
    
    print("="*60)
    print("NutriBudget BD - MVP Test")
    print("="*60)
    print(f"\nUser Profile:")
    print(f"  Age: {user['age']}")
    print(f"  Weight: {user['weight_kg']}kg")
    print(f"  Height: {user['height_cm']}cm")
    print(f"  Sex: {user['sex']}")
    print(f"  Activity Level: {user['activity_level']}")
    print(f"  Goal: {user['goal']}")
    print("\n" + "="*60)
    
    # Step 1: Initialize calculator
    print("\n[STEP 1] Initializing calculator...")
    calc = NutritionCalculator()
    print("✓ Calculator initialized")
    
    # Step 2: Calculate TDEE
    print("\n[STEP 2] Calculating TDEE...")
    tdee = calc.calculate_tdee(
        age=user["age"],
        weight_kg=user["weight_kg"],
        height_cm=user["height_cm"],
        sex=user["sex"],
        activity_level=user["activity_level"]
    )
    print(f"✓ TDEE: {tdee:.0f} kcal/day")
    
    # Step 3: Calculate targets
    print("\n[STEP 3] Calculating nutrition targets...")
    targets = calc.calculate_targets(
        tdee=tdee,
        weight_kg=user["weight_kg"],
        goal=user["goal"]
    )
    print(f"✓ Target Calories: {targets['target_calories']:.0f} kcal")
    print(f"✓ Target Protein: {targets['target_protein_g']:.1f}g")
    print(f"✓ Target Fat: {targets['target_fat_g']:.1f}g")
    print(f"✓ Target Carbs: {targets['target_carb_g']:.1f}g")
    
    # Step 4: Generate meal plan
    print("\n[STEP 4] Generating meal plan...")
    planner = MealPlanner(calc)
    plan = planner.generate_plan(
        target_calories=targets["target_calories"],
        target_protein_g=targets["target_protein_g"],
        tolerance_calories=100,
        tolerance_protein=5,
    )
    
    if not plan:
        print("✗ ERROR: Could not generate meal plan")
        return False
    
    print(f"✓ Generated plan with {len(plan)} foods")
    
    # Step 5: Calculate plan totals
    print("\n[STEP 5] Calculating plan totals...")
    plan_totals = planner.calculate_plan_totals(plan)
    print(f"✓ Total Calories: {plan_totals['total_calories']:.0f} kcal")
    print(f"✓ Total Protein: {plan_totals['total_protein_g']:.1f}g")
    
    # Step 6: Generate and display report
    print("\n[STEP 6] Generating report...")
    reporter = MealPlanReport(calc)
    
    print("\n" + "="*60)
    reporter.print_plan(plan, plan_totals)
    print("\n" + "="*60)
    
    print("\n✓ MVP Test PASSED - All systems operational!")
    return True


if __name__ == "__main__":
    success = test_mvp()
    sys.exit(0 if success else 1)
