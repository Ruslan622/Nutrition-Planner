"""
Trace micronutrient calculations step by step
Shows EXACTLY which foods contribute which micronutrients
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from core.calculator import NutritionCalculator
from core.planner import MealPlanner

calc = NutritionCalculator()
planner = MealPlanner(calc)

# Generate meal plan
user = {'age': 28, 'weight_kg': 75, 'height_cm': 180, 'sex': 'M', 'activity_level': 3, 'goal': 'maintenance'}
tdee = calc.calculate_tdee(age=user['age'], weight_kg=user['weight_kg'], height_cm=user['height_cm'], sex=user['sex'], activity_level=user['activity_level'])
targets = calc.calculate_targets(tdee=tdee, weight_kg=user['weight_kg'], goal=user['goal'])

print("=" * 90)
print("MICRONUTRIENT CALCULATION TRACE")
print("=" * 90)

plan = planner.generate_plan(
    target_calories=targets['target_calories'],
    target_protein_g=targets['target_protein_g'],
    tolerance_calories=150,
    tolerance_protein=10,
    enforce_variety=True,
)

print("\n📋 USER'S MEAL PLAN:")
print("-" * 90)
print(f"Target Calories: {targets['target_calories']} kcal")
print(f"Target Protein: {targets['target_protein_g']:.1f}g")
print()

# Show each food in the plan with its micronutrients
print("🍽️  INDIVIDUAL FOODS IN PLAN:")
print("-" * 90)

iron_sum = 0
calcium_sum = 0
vitamin_d_sum = 0
vitamin_c_sum = 0
potassium_sum = 0

for i, item in enumerate(plan, 1):
    food_key = item['food']
    quantity = item['quantity_g']
    food_name = calc.get_food_name(food_key)
    
    print(f"\n{i}. {food_name}")
    print(f"   Quantity: {quantity:.0f}g")
    print(f"   Calories: {item['calories']:.1f} kcal | Protein: {item['protein_g']:.1f}g")
    print(f"   Micronutrients:")
    print(f"     • Iron:      {item.get('iron_mg', 0):>6.2f} mg")
    print(f"     • Calcium:   {item.get('calcium_mg', 0):>6.1f} mg")
    print(f"     • Vitamin D: {item.get('vitamin_d_mcg', 0):>6.2f} mcg")
    print(f"     • Vitamin C: {item.get('vitamin_c_mg', 0):>6.2f} mg")
    print(f"     • Potassium: {item.get('potassium_mg', 0):>6.1f} mg")
    
    # Accumulate totals
    iron_sum += item.get('iron_mg', 0)
    calcium_sum += item.get('calcium_mg', 0)
    vitamin_d_sum += item.get('vitamin_d_mcg', 0)
    vitamin_c_sum += item.get('vitamin_c_mg', 0)
    potassium_sum += item.get('potassium_mg', 0)

# Show calculation formula for one food
print("\n\n📐 HOW CALCULATION WORKS (Example: Rice):")
print("-" * 90)
rice_data = calc.food_data['rice']
example_qty = 300
multiplier = example_qty / 100

print(f"Rice per 100g (from food_macros.json):")
print(f"  • Iron: {rice_data['iron_mg_per_100']} mg")
print(f"  • Calcium: {rice_data['calcium_mg_per_100']} mg")
print(f"  • Vitamin D: {rice_data['vitamin_d_mcg_per_100']} mcg")
print(f"  • Vitamin C: {rice_data['vitamin_c_mg_per_100']} mg")
print(f"  • Potassium: {rice_data['potassium_mg_per_100']} mg")

print(f"\nFor {example_qty}g of rice:")
print(f"  Multiplier = {example_qty}g ÷ 100g = {multiplier}")
print(f"  • Iron:      {rice_data['iron_mg_per_100']} × {multiplier} = {rice_data['iron_mg_per_100'] * multiplier:.2f} mg")
print(f"  • Calcium:   {rice_data['calcium_mg_per_100']} × {multiplier} = {rice_data['calcium_mg_per_100'] * multiplier:.1f} mg")
print(f"  • Vitamin D: {rice_data['vitamin_d_mcg_per_100']} × {multiplier} = {rice_data['vitamin_d_mcg_per_100'] * multiplier:.2f} mcg")
print(f"  • Vitamin C: {rice_data['vitamin_c_mg_per_100']} × {multiplier} = {rice_data['vitamin_c_mg_per_100'] * multiplier:.2f} mg")
print(f"  • Potassium: {rice_data['potassium_mg_per_100']} × {multiplier} = {rice_data['potassium_mg_per_100'] * multiplier:.1f} mg")

# Show totals
print("\n\n✅ DAILY TOTALS (Sum of all foods in the plan):")
print("-" * 90)
totals = planner.calculate_plan_totals(plan)
print(f"Iron:      {iron_sum:.2f} mg  (RDA: 8-18 mg)")
print(f"Calcium:   {calcium_sum:.1f} mg  (RDA: 1000 mg)")
print(f"Vitamin D: {vitamin_d_sum:.2f} mcg  (RDA: 15 mcg)")
print(f"Vitamin C: {vitamin_c_sum:.2f} mg  (RDA: 75-90 mg)")
print(f"Potassium: {potassium_sum:.1f} mg  (RDA: 2600-3400 mg)")

print("\n✓ These values are NOT random - they come from YOUR specific meal plan!")
print("✓ Each micronutrient is calculated from the actual quantities of foods in the plan")
print("=" * 90)
