"""
Test Cost Optimization Pipeline (STEP 10-16)
Tests: price loading, normalization, cost calculation, and budget-aware optimization.

Workflow:
1. Load prices
2. Generate nutritional plan
3. Calculate cost
4. Compare budget modes
5. Generate optimized plans
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from core.calculator import NutritionCalculator
from core.planner import MealPlanner
from core.cost_calculator import CostCalculator
from core.optimizer import Optimizer
from scraper.price_manager import PriceManager
from plans.report import MealPlanReport


def test_price_system():
    """Test STEP 10-12: Price loading and normalization."""
    print("\n" + "="*80)
    print("STEP 10-12: PRICE SYSTEM & NORMALIZATION")
    print("="*80)
    
    # Initialize calculator to get food data
    calc = NutritionCalculator()
    food_data = calc.food_data
    
    # Initialize price manager
    print("\n[1] Loading prices...")
    pm = PriceManager(food_data=food_data)
    print(f"✓ Loaded {len(pm.raw_prices)} foods")
    
    # Show normalization in action
    print("\n[2] Normalizing prices to BDT/100g...")
    pm.print_price_summary()
    
    # Show rankings
    print("\n[3] Foods ranked by price (cheapest first):")
    rankings = pm.rank_by_price()
    for food, price in rankings[:5]:
        raw_price, raw_unit = pm.get_raw_price(food)
        print(f"   {food:12} {price:8.2f} BDT/100g  (raw: {raw_price} {raw_unit})")
    
    return pm


def test_cost_calculation(calc, planner, pm):
    """Test STEP 13: Cost calculation on a real plan."""
    print("\n" + "="*80)
    print("STEP 13: COST CALCULATION")
    print("="*80)
    
    # Create user profile
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
    
    print(f"\nUser Profile: {user['weight_kg']}kg, Activity Level {user['activity_level']}")
    print(f"TDEE: {tdee:.0f} kcal")
    print(f"Targets: {targets['target_calories']:.0f} cal | {targets['target_protein_g']:.1f}g protein")
    
    # Generate plan
    print("\n[1] Generating nutritional plan...")
    plan = planner.generate_plan(
        target_calories=targets["target_calories"],
        target_protein_g=targets["target_protein_g"],
        tolerance_calories=150,
        tolerance_protein=10,
        enforce_variety=True,
    )
    
    if not plan:
        print("✗ Failed to generate plan")
        return None
    
    print(f"✓ Generated plan with {len(plan)} foods")
    
    # Calculate nutritional totals
    totals = planner.calculate_plan_totals(plan)
    
    # Calculate costs
    print("\n[2] Calculating costs...")
    cc = CostCalculator(pm)
    cost_info = cc.calculate_plan_cost(plan)
    
    print(f"✓ Daily Cost: {cost_info['total_cost_bdt']:.2f} BDT")
    print(f"✓ Monthly Cost: {cc.calculate_monthly_cost(plan):.2f} BDT")
    
    return plan, totals, cc


def test_protein_per_taka(plan, cc):
    """Test STEP 14: Protein-per-Taka metric."""
    print("\n" + "="*80)
    print("STEP 14: PROTEIN-PER-TAKA METRIC (Cost Efficiency)")
    print("="*80)
    
    ppt = cc.calculate_protein_per_taka(plan)
    ppt_100 = cc.calculate_protein_per_100_taka(plan)
    cpt = cc.calculate_calories_per_taka(plan)
    cost_per_1000 = cc.calculate_cost_per_1000cal(plan)
    
    print(f"\n[KEY METRICS]")
    print(f"  Protein per 1 BDT:   {ppt:.3f}g")
    print(f"  Protein per 100 BDT: {ppt_100:.1f}g")
    print(f"  Calories per 1 BDT:  {cpt:.3f} kcal")
    print(f"  Cost per 1000 kcal:  {cost_per_1000:.2f} BDT")
    
    # Cost breakdown
    print(f"\n[COST BREAKDOWN]")
    cost_analysis = cc.print_cost_analysis(plan)
    print(cost_analysis)


def test_optimizer(calc, planner, pm, cc, target_calories, target_protein):
    """Test STEP 15-16: Optimizer with budget modes."""
    print("\n" + "="*80)
    print("STEP 15-16: COST-OPTIMIZED PLANS (BUDGET MODES)")
    print("="*80)
    
    # Initialize optimizer
    opt = Optimizer(calc, planner, pm, cc)
    
    # Generate plans for all budget modes
    print("\n[1] Generating optimized plans for all budget modes...")
    plans_by_mode = opt.generate_plans_all_modes(
        target_calories=target_calories,
        target_protein_g=target_protein,
        tolerance_calories=150,
        tolerance_protein=10,
    )
    
    if not plans_by_mode:
        print("✗ Failed to generate any plans")
        return
    
    print(f"✓ Generated {len(plans_by_mode)} plans")
    
    # Print comparison
    print("\n[2] Budget Mode Comparison:")
    comparison = opt.print_optimization_summary(plans_by_mode)
    print(comparison)
    
    # Show details for each mode
    print("\n[3] Detailed Breakdown:")
    for mode in ["cheapest", "balanced", "premium"]:
        if mode in plans_by_mode:
            plan, metrics = plans_by_mode[mode]
            print(f"\n{'─'*80}")
            print(f"MODE: {mode.upper()}")
            print(f"{'─'*80}")
            print(f"Daily Cost:      {metrics['daily_cost_bdt']:.2f} BDT")
            print(f"Monthly Cost:    {metrics['monthly_cost_bdt']:.2f} BDT")
            print(f"Total Protein:   {metrics['total_protein_g']:.1f}g")
            print(f"Total Calories:  {metrics['total_calories']:.0f} kcal")
            print(f"Protein/100BDT:  {metrics['protein_per_100_taka']:.1f}g")
            print(f"Kcal/100BDT:     {metrics['calories_per_100_taka']:.0f} kcal")
            print(f"Quality Score:   {metrics['combined_score']:.3f}")
            print(f"Foods: {len(plan)}")
            
            # List foods for cheapest mode
            if mode == "cheapest":
                print(f"\nFoods in {mode} plan:")
                for item in sorted(plan, key=lambda x: cc.pm.get_price_for_quantity(x['food'], x['quantity_g']), reverse=True):
                    cost = cc.pm.get_price_for_quantity(item['food'], item['quantity_g'])
                    print(f"  • {item['food']:12} {item['quantity_g']:6.0f}g  →  {cost:7.2f} BDT")


def main():
    """Run complete cost optimization test."""
    print("\n" + "="*80)
    print("NUTRIBUDGET BD — COST OPTIMIZATION PIPELINE TEST")
    print("STEPS 10-16: Price System → Optimizer")
    print("="*80)
    
    # Initialize core components
    print("\n[SETUP] Initializing components...")
    calc = NutritionCalculator()
    planner = MealPlanner(calc)
    
    # STEP 10-12: Price system
    pm = test_price_system()
    
    # STEP 13-14: Cost calculation
    result = test_cost_calculation(calc, planner, pm)
    if not result:
        return False
    
    plan, totals, cc = result
    test_protein_per_taka(plan, cc)
    
    # STEP 15-16: Optimizer with budget modes
    test_optimizer(calc, planner, pm, cc, totals['total_calories'], totals['total_protein_g'])
    
    # Final summary
    print("\n" + "="*80)
    print("✓ COST OPTIMIZATION PIPELINE COMPLETE")
    print("="*80)
    print("\nNEXT STEPS:")
    print("  • STEP 17: Add scraper integration to fetch live prices")
    print("  • STEP 18: Build UI/API layer")
    print("  • STEP 19: Add user preferences & favorites")
    print("\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
