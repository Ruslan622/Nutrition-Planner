"""
Debug serving granularity rounding issue.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.calculator import NutritionCalculator
from core.planner import MealPlanner

calc = NutritionCalculator()
planner = MealPlanner(calc)

targets = calc.calculate_targets(2697, 75, "maintenance")

# Generate plan without variety
plan_no_var = planner.generate_plan(
    target_calories=targets["target_calories"],
    target_protein_g=targets["target_protein_g"],
    tolerance_calories=150,
    tolerance_protein=10,
    enforce_variety=False,
)

print("[1] Original plan (before rounding):")
total_cal = 0
total_pro = 0
for item in plan_no_var:
    total_cal += item["calories"]
    total_pro += item["protein_g"]
    print(f"   {item['food']:12} {item['quantity_g']:8.1f}g  →  {item['calories']:7.1f} cal, {item['protein_g']:6.1f}g pro")

print(f"Totals: {total_cal:.1f} cal, {total_pro:.1f}g pro")
print(f"Target: {targets['target_calories']:.1f} cal, {targets['target_protein_g']:.1f}g pro")
print(f"Within tolerance? {abs(total_cal - targets['target_calories']) <= 150} cal, {abs(total_pro - targets['target_protein_g']) <= 10} pro")

# Now apply rounding
print("\n[2] After _apply_serving_granularity rounding:")
rounded_plan = planner._apply_serving_granularity(plan_no_var)
total_cal_rounded = 0
total_pro_rounded = 0
for item in rounded_plan:
    total_cal_rounded += item["calories"]
    total_pro_rounded += item["protein_g"]
    print(f"   {item['food']:12} {item['quantity_g']:8.1f}g ({item.get('num_servings', 1):.0f} servings)  →  {item['calories']:7.1f} cal, {item['protein_g']:6.1f}g pro")

print(f"Totals: {total_cal_rounded:.1f} cal, {total_pro_rounded:.1f}g pro")
print(f"Target: {targets['target_calories']:.1f} cal, {targets['target_protein_g']:.1f}g pro")
print(f"Within tolerance? {abs(total_cal_rounded - targets['target_calories']) <= 150} cal, {abs(total_pro_rounded - targets['target_protein_g']) <= 10} pro")
