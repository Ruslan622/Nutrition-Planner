"""
Debug full optimizer flow.
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

print("[1] Calling generate_optimized_plan...")
plan, metrics = opt.generate_optimized_plan(
    target_calories=targets["target_calories"],
    target_protein_g=targets["target_protein_g"],
    target_fat_g=targets["target_fat_g"],
    target_carb_g=targets["target_carb_g"],
    tolerance_calories=150,
    tolerance_protein=10,
    budget_mode="balanced",
    enforce_variety=True
)

print(f"Result: plan={len(plan) if plan else 0}, metrics={bool(metrics)}")

if plan:
    print(f"\nPlan returned:")
    for item in plan:
        print(f"  {item['food']:12} {item['quantity_g']:6.0f}g")
    print(f"\nMetrics: {metrics}")
else:
    print("No plan returned - debugging...")
    
    # Step through manually
    print("\n[2] Testing candidate generation...")
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
    print(f"Candidates: {len(candidates)}")
    
    if not candidates:
        print("ERROR: No candidates generated!")
    else:
        print("\n[3] Testing plan scoring...")
        scored = opt._score_plans(candidates, "balanced", targets["target_protein_g"], targets["target_calories"])
        print(f"Scored plans: {len(scored)}")
        
        for i, (plan, score, metrics) in enumerate(scored):
            print(f"\nPlan {i+1}:")
            print(f"  Score: {score:.3f}")
            print(f"  Metrics: {metrics}")
