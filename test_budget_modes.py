"""
Test Budget Mode Differentiation
Generates formatted receipt outputs for each budget mode.
Outputs written to output/meal_plan_*.txt files
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.calculator import NutritionCalculator
from core.planner import MealPlanner
from core.cost_calculator import CostCalculator
from core.optimizer import Optimizer
from scraper.price_manager import PriceManager
from plans.receipt_formatter import ReceiptFormatter


def generate_formatted_output(output_dir: str = "output"):
    """Generate formatted meal plan receipts for all budget modes."""
    
    output_path = Path(__file__).parent / output_dir
    output_path.mkdir(exist_ok=True)
    
    print("\n" + "="*80)
    print("BUDGET MODE DIFFERENTIATION TEST")
    print("Generating formatted receipts for all budget modes")
    print("="*80 + "\n")
    
    # Initialize components
    print("[SETUP] Initializing components...")
    calc = NutritionCalculator()
    planner = MealPlanner(calc)
    pm = PriceManager(food_data=calc.food_data)
    cc = CostCalculator(pm)
    opt = Optimizer(calc, planner, pm, cc)
    formatter = ReceiptFormatter(calc, pm)
    
    # User profile
    user = {
        "age": 28,
        "weight_kg": 75,
        "height_cm": 180,
        "sex": "M",
        "activity_level": 3,
        "goal": "maintenance",
    }
    
    # Calculate targets
    tdee = calc.calculate_tdee(
        age=user["age"],
        weight_kg=user["weight_kg"],
        height_cm=user["height_cm"],
        sex=user["sex"],
        activity_level=user["activity_level"]
    )
    
    targets = calc.calculate_targets(tdee=tdee, weight_kg=user["weight_kg"], goal=user["goal"])
    
    print(f"User: {user['weight_kg']}kg, Activity Level {user['activity_level']}, Goal: {user['goal']}")
    print(f"TDEE: {tdee:.0f} kcal")
    print(f"Targets: {targets['target_calories']:.0f} cal | {targets['target_protein_g']:.1f}g protein\n")
    
    # Generate optimized plans for all modes
    print("[GENERATE] Generating optimized plans for all budget modes...")
    plans_by_mode = opt.generate_plans_all_modes(
        target_calories=targets["target_calories"],
        target_protein_g=targets["target_protein_g"],
        target_fat_g=targets["target_fat_g"],
        target_carb_g=targets["target_carb_g"],
        tolerance_calories=150,
        tolerance_protein=10,
    )
    
    if not plans_by_mode:
        print("✗ ERROR: No plans generated")
        return False
    
    print(f"✓ Generated {len(plans_by_mode)} plans\n")
    
    # Generate and save receipts for each mode
    print("[OUTPUT] Generating formatted PDF receipts...\n")
    
    for mode in ["cheapest", "balanced", "premium"]:
        if mode not in plans_by_mode:
            continue
        
        plan, metrics = plans_by_mode[mode]
        totals = planner.calculate_plan_totals(plan)
        cost_info = cc.calculate_plan_cost(plan)
        
        # Save as PDF
        filename = f"meal_plan_{mode}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = output_path / filename
        
        success = formatter.save_meal_receipt_pdf(
            filepath=str(filepath),
            plan=plan,
            totals=totals,
            cost_info=cost_info,
            metrics=metrics,
            user_profile=user
        )
        
        if success:
            print(f"✓ Saved: {filename}")
            print(f"  Cost: {metrics['daily_cost_bdt']:.2f} BDT/day")
            print(f"  Quality: {metrics.get('avg_protein_quality', 5.0):.1f}/10")
            print(f"  Foods: {metrics['num_foods']} different foods\n")
        else:
            print(f"✗ Failed to save: {filename}\n")
    
    # Generate comparison receipt
    print("[COMPARISON] Generating budget mode comparison...")
    success = formatter.save_budget_comparison_pdf(
        filepath=str(output_path / f"budget_comparison_{datetime.now().strftime('%Y%m%d')}.pdf"),
        plans_by_mode=plans_by_mode
    )
    
    if success:
        comp_filename = f"budget_comparison_{datetime.now().strftime('%Y%m%d')}.pdf"
        print(f"✓ Saved: {comp_filename}\n")
    else:
        print("✗ Failed to save comparison\n")
    
    # Print summary
    print("="*80)
    print("SUMMARY: Budget Modes Generated Successfully!")
    print("="*80)
    
    print("\n📋 PDF FILES GENERATED:")
    for mode in ["cheapest", "balanced", "premium"]:
        if mode in plans_by_mode:
            print(f"  • meal_plan_{mode}_*.pdf")
    print(f"  • budget_comparison_*.pdf")
    
    print(f"\n📍 Location: {output_path}\n")
    
    # Show differences
    print("="*80)
    print("PLAN DIFFERENCES")
    print("="*80)
    
    if len(plans_by_mode) == 3:
        cheapest_plan, cheapest_metrics = plans_by_mode["cheapest"]
        balanced_plan, balanced_metrics = plans_by_mode["balanced"]
        premium_plan, premium_metrics = plans_by_mode["premium"]
        
        print("\n[CHEAPEST PLAN]")
        print(f"  Daily Cost: {cheapest_metrics['daily_cost_bdt']:.2f} BDT")
        print(f"  Foods: {', '.join([item['food'] for item in cheapest_plan])}")
        print(f"  Quality Score: {cheapest_metrics.get('avg_protein_quality', 0):.1f}/10")
        
        print("\n[BALANCED PLAN]")
        print(f"  Daily Cost: {balanced_metrics['daily_cost_bdt']:.2f} BDT")
        print(f"  Foods: {', '.join([item['food'] for item in balanced_plan])}")
        print(f"  Quality Score: {balanced_metrics.get('avg_protein_quality', 0):.1f}/10")
        
        print("\n[PREMIUM PLAN]")
        print(f"  Daily Cost: {premium_metrics['daily_cost_bdt']:.2f} BDT")
        print(f"  Foods: {', '.join([item['food'] for item in premium_plan])}")
        print(f"  Quality Score: {premium_metrics.get('avg_protein_quality', 0):.1f}/10")
        
        print("\n[COST DIFFERENCE]")
        cheapest_cost = cheapest_metrics['daily_cost_bdt']
        premium_cost = premium_metrics['daily_cost_bdt']
        diff = premium_cost - cheapest_cost
        diff_pct = (diff / cheapest_cost) * 100
        print(f"  Premium costs {diff:.2f} BDT more/day ({diff_pct:.1f}% increase)")
        print(f"  That's {diff*30:.2f} BDT more per month")
        
        # Quality difference
        cheapest_quality = cheapest_metrics.get('avg_protein_quality', 0)
        premium_quality = premium_metrics.get('avg_protein_quality', 0)
        quality_diff = premium_quality - cheapest_quality
        print(f"\n[QUALITY DIFFERENCE]")
        print(f"  Premium protein quality: {premium_quality:.1f}/10")
        print(f"  Cheapest protein quality: {cheapest_quality:.1f}/10")
        print(f"  Difference: +{quality_diff:.1f} points")
    
    print("\n" + "="*80 + "\n")
    
    return True


if __name__ == "__main__":
    success = generate_formatted_output()
    sys.exit(0 if success else 1)
