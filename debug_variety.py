"""
Debug variety constraint issue.
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
print("[1] Generate plan WITHOUT variety constraint...")
plan = planner.generate_plan(
    target_calories=targets["target_calories"],
    target_protein_g=targets["target_protein_g"],
    tolerance_calories=150,
    tolerance_protein=10,
    enforce_variety=False,
)

print(f"✓ Got plan with {len(plan)} foods")

# Now check if this plan passes variety check
print("\n[2] Check if this plan passes variety check...")
result = planner._check_variety(plan)
print(f"Variety check result: {result}")

# Show categories
print("\n[3] Plan categories:")
categories = set()
for item in plan:
    cat = item.get("category", "unknown")
    categories.add(cat)
    print(f"   {item['food']:12} -> {cat}")

print(f"\nCategories in plan: {categories}")

# Check variety logic
has_protein = any(cat in ["protein", "protein_carb"] for cat in categories)
has_carb = any(cat in ["carb", "protein_carb"] for cat in categories)
print(f"Has protein source: {has_protein}")
print(f"Has carb source: {has_carb}")

# Check dominance
total_cals = sum(item["calories"] for item in plan)
print(f"\n[4] Dominance check (max 2 foods >35% each):")
dominant_count = 0
for item in plan:
    pct = (item["calories"] / total_cals) * 100
    is_dominant = item["calories"] / total_cals > 0.35
    print(f"   {item['food']:12} {pct:5.1f}% {'[DOMINANT]' if is_dominant else ''}")
    if is_dominant:
        dominant_count += 1

print(f"Dominant count: {dominant_count} (max allowed: 2)")
