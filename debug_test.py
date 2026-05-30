"""
Debug test - check what's failing in the meal planner.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.calculator import NutritionCalculator
from core.planner import MealPlanner

# Test 1: Check calculator works
print("[1] Testing NutritionCalculator...")
calc = NutritionCalculator()
print(f"✓ Foods loaded: {len(calc.available_foods())}")

# Test 2: Check TDEE calculation
print("\n[2] Testing TDEE...")
tdee = calc.calculate_tdee(28, 75, 180, "M", 3)
print(f"✓ TDEE: {tdee}")

# Test 3: Check targets
print("\n[3] Testing targets...")
targets = calc.calculate_targets(tdee, 75, "maintenance")
print(f"✓ Targets: {targets}")

# Test 4: Initialize planner
print("\n[4] Testing MealPlanner...")
planner = MealPlanner(calc)
print("✓ Planner initialized")

# Test 5: Try generating a plan
print("\n[5] Generating plan...")
plan = planner.generate_plan(
    target_calories=targets["target_calories"],
    target_protein_g=targets["target_protein_g"],
    tolerance_calories=100,
    tolerance_protein=5,
    enforce_variety=True,
)

if plan:
    print(f"✓ Plan generated with {len(plan)} foods:")
    for item in plan:
        print(f"   {item['food']:12} {item['quantity_g']:6.0f}g")
else:
    print("✗ Plan generation failed")
    
    # Debug: Try without variety
    print("\n[5b] Trying without variety constraint...")
    plan = planner.generate_plan(
        target_calories=targets["target_calories"],
        target_protein_g=targets["target_protein_g"],
        tolerance_calories=150,
        tolerance_protein=10,
        enforce_variety=False,
    )
    
    if plan:
        print(f"✓ Plan generated with {len(plan)} foods:")
        for item in plan:
            print(f"   {item['food']:12} {item['quantity_g']:6.0f}g")
    else:
        print("✗ Still failed")
        
        # Debug: Check what foods are available
        print("\n[5c] Available foods and constraints:")
        for food in calc.available_foods():
            constraints = calc.get_serving_constraints(food)
            macros = calc.get_food_macros(food, 100)
            print(f"   {food:12} - min:{constraints['min_serving_g']} max:{constraints['max_serving_g']} - category: {macros['category']}")
