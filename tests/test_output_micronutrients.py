"""
Test that micronutrients are saved to output
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from core.calculator import NutritionCalculator
from core.planner import MealPlanner
from core.cost_calculator import CostCalculator
from scraper.price_manager import PriceManager
from plans.receipt_formatter import ReceiptFormatter

# Setup
calc = NutritionCalculator()
planner = MealPlanner(calc)
pm = PriceManager(food_data=calc.food_data)
cc = CostCalculator(pm)
formatter = ReceiptFormatter(calc, pm)

# Generate plan
user = {
    "age": 28,
    "weight_kg": 75,
    "height_cm": 180,
    "sex": "M",
    "activity_level": 3,
    "goal": "maintenance",
}

tdee = calc.calculate_tdee(
    age=user["age"],
    weight_kg=user["weight_kg"],
    height_cm=user["height_cm"],
    sex=user["sex"],
    activity_level=user["activity_level"]
)

targets = calc.calculate_targets(tdee=tdee, weight_kg=user["weight_kg"], goal=user["goal"])

plan = planner.generate_plan(
    target_calories=targets["target_calories"],
    target_protein_g=targets["target_protein_g"],
    tolerance_calories=150,
    tolerance_protein=10,
    enforce_variety=True,
)

totals = planner.calculate_plan_totals(plan)
cost_info = cc.calculate_plan_cost(plan)

# Format receipt
receipt = formatter.format_meal_receipt(
    plan=plan,
    totals=totals,
    cost_info=cost_info,
    user_profile=user,
)

# Check if micronutrients are in the receipt
if "MICRONUTRIENT" in receipt and "Iron:" in receipt:
    print("✓ Micronutrients ARE saved in output!")
    print("\nMicronutrient section from output:")
    print("=" * 70)
    for line in receipt.split("\n"):
        if "Iron:" in line or "Calcium:" in line or "Vitamin" in line or "Potassium:" in line:
            print(line)
else:
    print("✗ Micronutrients NOT found in output")
    print("\nReceipt content:")
    print(receipt)
