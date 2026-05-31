"""
Test meal-based receipt generation
Shows the new format_meal_plan_receipt method
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from core.calculator import NutritionCalculator
from core.planner import MealPlanner
from core.cost_calculator import CostCalculator
from scraper.price_manager import PriceManager
from plans.receipt_formatter import ReceiptFormatter

calc = NutritionCalculator()
planner = MealPlanner(calc)
pm = PriceManager(food_data=calc.food_data)
cc = CostCalculator(pm)
formatter = ReceiptFormatter(calc, pm)

# Generate meal plan
user = {
    'age': 28,
    'weight_kg': 75,
    'height_cm': 180,
    'sex': 'M',
    'activity_level': 3,
    'goal': 'maintenance',
}

tdee = calc.calculate_tdee(
    age=user['age'],
    weight_kg=user['weight_kg'],
    height_cm=user['height_cm'],
    sex=user['sex'],
    activity_level=user['activity_level']
)

targets = calc.calculate_targets(tdee=tdee, weight_kg=user['weight_kg'], goal=user['goal'])

# Generate daily plan
plan = planner.generate_plan(
    target_calories=targets['target_calories'],
    target_protein_g=targets['target_protein_g'],
    tolerance_calories=150,
    tolerance_protein=10,
    enforce_variety=True,
)

totals = planner.calculate_plan_totals(plan)
cost_info = cc.calculate_plan_cost(plan)

# Distribute to meals
meals = planner.distribute_to_meals(plan)

# Format and display
receipt = formatter.format_meal_plan_receipt(
    plan=plan,
    meals=meals,
    totals=totals,
    cost_info=cost_info,
    user_profile=user,
)

print(receipt)
