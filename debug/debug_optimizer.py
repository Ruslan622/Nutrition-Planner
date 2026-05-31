"""
Debug optimizer candidate generation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from core.calculator import NutritionCalculator
from core.planner import MealPlanner
from core.cost_calculator import CostCalculator
from core.optimizer import Optimizer
from scraper.price_manager import PriceManager

calc = NutritionCalculator()
planner = MealPlanner(calc)
pm = PriceManager(food_data=calc.food_data)
cc = CostCalculator(pm)
opt = Optimizer(calc, planner, pm, cc)

targets = calc.calculate_targets(2697, 75, "maintenance")

print("[1] Testing _generate_mode_specific_candidates...")
candidates = opt._generate_mode_specific_candidates(
    target_calories=targets["target_calories"],
    target_protein_g=targets["target_protein_g"],
    target_fat_g=targets["target_fat_g"],
    target_carb_g=targets["target_carb_g"],
    tolerance_calories=150,
    tolerance_protein=10,
    budget_mode="balanced",
    enforce_variety=True
)

print(f"Generated {len(candidates)} candidates")
for i, plan in enumerate(candidates):
    total_cal = sum(item["calories"] for item in plan)
    total_pro = sum(item["protein_g"] for item in plan)
    cost = cc.calculate_daily_cost(plan)
    print(f"\nCandidate {i+1}: {len(plan)} foods")
    print(f"  Calories: {total_cal:.0f} (target: {targets['target_calories']:.0f})")
    print(f"  Protein: {total_pro:.1f}g (target: {targets['target_protein_g']:.1f}g)")
    print(f"  Cost: {cost:.2f} BDT")
    for item in plan:
        print(f"    {item['food']:12} {item['quantity_g']:6.0f}g")
