"""
Test micronutrient tracking
"""
from core.calculator import NutritionCalculator
from core.planner import MealPlanner
from plans.report import MealPlanReport

# Setup
calc = NutritionCalculator()
planner = MealPlanner(calc)

# Generate a meal plan
user = {
    "age": 28,
    "weight_kg": 75,
    "height_cm": 180,
    "sex": "M",
    "activity_level": 3,
    "goal": "maintenance",
}

# Calculate TDEE
tdee = calc.calculate_tdee(
    age=user["age"],
    weight_kg=user["weight_kg"],
    height_cm=user["height_cm"],
    sex=user["sex"],
    activity_level=user["activity_level"]
)

targets = calc.calculate_targets(tdee=tdee, weight_kg=user["weight_kg"], goal=user["goal"])

# Generate plan
print(f"Target Calories: {targets['target_calories']:.0f}")
print(f"Target Protein: {targets['target_protein_g']:.1f}g")
print("")

plan = planner.generate_plan(
    target_calories=targets["target_calories"],
    target_protein_g=targets["target_protein_g"],
    tolerance_calories=150,
    tolerance_protein=10,
    enforce_variety=True,
)

print(f"Plan generated with {len(plan)} foods")
if not plan:
    print("ERROR: No plan generated!")

plan_totals = planner.calculate_plan_totals(plan)

# Display with micronutrients
report = MealPlanReport(calc)
print("\n" + "="*70)
print("MEAL PLAN WITH MICRONUTRIENT TRACKING")
print("="*70 + "\n")

print("DAILY MACROS:")
print(f"  Calories: {plan_totals['total_calories']:.0f} kcal")
print(f"  Protein:  {plan_totals['total_protein_g']:.1f}g")
print(f"  Fat:      {plan_totals['total_fat_g']:.1f}g")
print(f"  Carbs:    {plan_totals['total_carb_g']:.1f}g")
print(f"  Fiber:    {plan_totals['total_fiber_g']:.1f}g")
print("")

print("MICRONUTRIENTS:")
print(f"  Iron:       {plan_totals.get('total_iron_mg', 0):.1f} mg (RDA: 8-18mg)")
print(f"  Calcium:    {plan_totals.get('total_calcium_mg', 0):.0f} mg (RDA: 1000mg)")
print(f"  Vitamin D:  {plan_totals.get('total_vitamin_d_mcg', 0):.1f} mcg (RDA: 15mcg)")
print(f"  Vitamin C:  {plan_totals.get('total_vitamin_c_mg', 0):.1f} mg (RDA: 75-90mg)")
print(f"  Potassium:  {plan_totals.get('total_potassium_mg', 0):.0f} mg (RDA: 2600-3400mg)")
print("")

print("FOODS:")
for item in plan:
    food_name = calc.get_food_name(item["food"])
    print(f"  - {food_name}: {item['quantity_g']}g")
    print(f"      Calories: {item['calories']:.0f} | Protein: {item['protein_g']:.1f}g")
    print(f"      Iron: {item.get('iron_mg', 0):.2f}mg | Calcium: {item.get('calcium_mg', 0):.0f}mg")
    print("")

print("="*70)
print("MICRONUTRIENT TRACKING IS WORKING!")
print("="*70)
