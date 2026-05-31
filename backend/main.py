"""
NutriBudget BD - Main Entry Point
Flow: Input → Calculator → Planner → Report

NO scraping here. Pure nutrition planning MVP.
"""

from core.calculator import NutritionCalculator
from core.planner import MealPlanner
from plans.report import MealPlanReport


def get_user_input() -> dict:
    """
    Get user profile from input.
    
    Returns:
        Dict with age, weight_kg, height_cm, sex, activity_level, goal
    """
    print("\n" + "="*50)
    print("NutriBudget BD - Nutrition Planner")
    print("="*50 + "\n")
    
    # Get basic info
    age = int(input("Age (years): "))
    weight_kg = float(input("Weight (kg): "))
    height_cm = float(input("Height (cm): "))
    
    sex = input("Sex (M/F): ").upper()
    while sex not in ["M", "F"]:
        sex = input("Please enter M or F: ").upper()
    
    # Activity level
    print("\nActivity Level:")
    print("  1 = Sedentary (desk job, no exercise)")
    print("  2 = Lightly active (light exercise 1-3 days/week)")
    print("  3 = Moderately active (moderate exercise 3-5 days/week)")
    print("  4 = Very active (hard exercise 6-7 days/week)")
    print("  5 = Extra active (physical job + daily training)")
    
    activity_level = int(input("Choose activity level (1-5): "))
    while activity_level not in [1, 2, 3, 4, 5]:
        activity_level = int(input("Please enter 1-5: "))
    
    # Goal
    print("\nGoal:")
    print("  1 = Maintenance (sustain current weight)")
    print("  2 = Fat Loss (500 kcal deficit, ~0.5 kg loss/week)")
    print("  3 = Muscle Gain (300 kcal surplus, lean bulk)")
    
    goal_choice = input("Choose goal (1-3): ")
    goal_map = {"1": "maintenance", "2": "loss", "3": "gain"}
    goal = goal_map.get(goal_choice, "maintenance")
    
    return {
        "age": age,
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "sex": sex,
        "activity_level": activity_level,
        "goal": goal,
    }


def main():
    """Main workflow: Input → Calculate → Plan → Report."""
    
    # Step 1: Get user input
    user = get_user_input()
    print("\n" + "="*50)
    print("Calculating your nutrition plan...")
    print("="*50 + "\n")
    
    # Step 2: Initialize calculator
    calc = NutritionCalculator()
    
    # Step 3: Calculate TDEE and targets
    tdee = calc.calculate_tdee(
        age=user["age"],
        weight_kg=user["weight_kg"],
        height_cm=user["height_cm"],
        sex=user["sex"],
        activity_level=user["activity_level"]
    )
    
    targets = calc.calculate_targets(
        tdee=tdee,
        weight_kg=user["weight_kg"],
        goal=user["goal"]
    )
    
    print(f"TDEE: {tdee:.0f} kcal/day")
    print(f"Target Calories: {targets['target_calories']:.0f} kcal")
    print(f"Target Protein: {targets['target_protein_g']:.1f}g")
    print(f"Target Fat: {targets['target_fat_g']:.1f}g")
    print(f"Target Carbs: {targets['target_carb_g']:.1f}g\n")
    
    # Step 4: Generate meal plan
    planner = MealPlanner(calc)
    plan = planner.generate_plan(
        target_calories=targets["target_calories"],
        target_protein_g=targets["target_protein_g"],
        tolerance_calories=100,
        tolerance_protein=5,
    )
    
    if not plan:
        print("ERROR: Could not generate a meal plan meeting your targets.")
        print("Try adjusting your goals or activity level.\n")
        return
    
    # Step 5: Calculate totals and report
    plan_totals = planner.calculate_plan_totals(plan)
    
    # Step 6: Display report
    reporter = MealPlanReport(calc)
    reporter.print_plan(plan, plan_totals)
    
    # Summary
    print("\n" + "="*50)
    print(reporter.format_quick_summary(plan_totals))
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
