"""
Report v2
Formats and prints meal plans with meal distribution.
Shows: breakfast, lunch, dinner with nutrition breakdown.
"""

from typing import List, Dict


class MealPlanReport:
    """Format and display meal plans with meal distribution."""
    
    def __init__(self, calculator):
        """
        Initialize report formatter.
        
        Args:
            calculator: NutritionCalculator instance (for food names)
        """
        self.calc = calculator
    
    def format_plan(self, plan: List[Dict], totals: Dict) -> str:
        """
        Format a daily meal plan for display with human-readable portions.
        
        Args:
            plan: List of meal items from MealPlanner.generate_plan()
            totals: Dict from MealPlanner.calculate_plan_totals()
            
        Returns:
            Formatted string ready to print
        """
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("DAILY MEAL PLAN")
        lines.append("=" * 60)
        lines.append("")
        
        # Daily summary
        lines.append("DAILY TARGETS:")
        lines.append(f"  Calories: {totals['total_calories']:.0f} kcal")
        lines.append(f"  Protein:  {totals['total_protein_g']:.1f}g")
        lines.append(f"  Fat:      {totals['total_fat_g']:.1f}g")
        lines.append(f"  Carbs:    {totals['total_carb_g']:.1f}g")
        lines.append(f"  Fiber:    {totals['total_fiber_g']:.1f}g")
        lines.append("")
        
        # Micronutrients
        lines.append("MICRONUTRIENTS:")
        lines.append(f"  Iron:       {totals.get('total_iron_mg', 0):.1f} mg (RDA: 8-18mg)")
        lines.append(f"  Calcium:    {totals.get('total_calcium_mg', 0):.0f} mg (RDA: 1000mg)")
        lines.append(f"  Vitamin D:  {totals.get('total_vitamin_d_mcg', 0):.1f} mcg (RDA: 15mcg)")
        lines.append(f"  Vitamin C:  {totals.get('total_vitamin_c_mg', 0):.1f} mg (RDA: 75-90mg)")
        lines.append(f"  Potassium:  {totals.get('total_potassium_mg', 0):.0f} mg (RDA: 2600-3400mg)")
        lines.append("")
        
        # Foods list with human-readable portions
        lines.append("FOODS TO EAT:")
        for item in plan:
            food_name = self.calc.get_food_name(item["food"])
            qty = item["quantity_g"]
            num_servings = item.get("num_servings", 1)
            serving_info = self.calc.get_serving_info(item["food"])
            category = item.get("category", "other")
            
            # Build portion string
            serving_unit = serving_info["serving_unit"]
            if serving_unit == "piece":
                portion_str = f"{num_servings} {serving_unit}s" if num_servings > 1 else f"{num_servings} {serving_unit}"
            elif serving_unit == "cup":
                portion_str = f"{num_servings} cup" if num_servings == 1 else f"{num_servings} cups"
            elif serving_unit == "slice":
                portion_str = f"{num_servings} slice" if num_servings == 1 else f"{num_servings} slices"
            else:
                portion_str = f"{qty}g"
            
            lines.append(f"  • {food_name}: {portion_str} ({qty}g) [{category}]")
            lines.append(f"      ↳ {item['calories']:.0f} cal | {item['protein_g']:.1f}g protein | {item['carb_g']:.1f}g carbs")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def format_plan_with_meals(self, meals: Dict, totals: Dict) -> str:
        """
        Format meal plan distributed across breakfast, lunch, dinner.
        
        Args:
            meals: Dict from MealPlanner.distribute_to_meals()
            totals: Dict from MealPlanner.calculate_plan_totals()
            
        Returns:
            Formatted string with meal distribution
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("DAILY MEAL PLAN - DISTRIBUTED ACROSS MEALS")
        lines.append("=" * 70)
        lines.append("")
        
        # Daily summary
        lines.append("DAILY TARGETS:")
        lines.append(f"  Calories: {totals['total_calories']:.0f} kcal  |  "
                    f"Protein: {totals['total_protein_g']:.1f}g  |  "
                    f"Carbs: {totals['total_carb_g']:.1f}g")
        lines.append("")
        
        # Micronutrients summary
        lines.append("MICRONUTRIENTS:")
        lines.append(f"  Iron: {totals.get('total_iron_mg', 0):.1f}mg  |  "
                    f"Calcium: {totals.get('total_calcium_mg', 0):.0f}mg  |  "
                    f"Vitamin D: {totals.get('total_vitamin_d_mcg', 0):.1f}mcg  |  "
                    f"Vitamin C: {totals.get('total_vitamin_c_mg', 0):.1f}mg")
        lines.append("")
        
        # Breakfast
        if meals.get("breakfast", {}).get("foods"):
            bfast = meals["breakfast"]
            bfast_pct = (bfast["calories"] / totals['total_calories']) * 100 if totals['total_calories'] > 0 else 0
            lines.append("🌅 BREAKFAST")
            lines.append(f"   Calories: {bfast['calories']:.0f} ({bfast_pct:.0f}%) | Protein: {bfast['protein_g']:.1f}g")
            for item in bfast["foods"]:
                food_name = self.calc.get_food_name(item["food"])
                lines.append(f"   • {food_name}: {item['quantity_g']}g")
            lines.append("")
        
        # Lunch
        if meals.get("lunch", {}).get("foods"):
            lunch = meals["lunch"]
            lunch_pct = (lunch["calories"] / totals['total_calories']) * 100 if totals['total_calories'] > 0 else 0
            lines.append("🍽️  LUNCH")
            lines.append(f"   Calories: {lunch['calories']:.0f} ({lunch_pct:.0f}%) | Protein: {lunch['protein_g']:.1f}g")
            for item in lunch["foods"]:
                food_name = self.calc.get_food_name(item["food"])
                lines.append(f"   • {food_name}: {item['quantity_g']}g")
            lines.append("")
        
        # Dinner
        if meals.get("dinner", {}).get("foods"):
            dinner = meals["dinner"]
            dinner_pct = (dinner["calories"] / totals['total_calories']) * 100 if totals['total_calories'] > 0 else 0
            lines.append("🍲 DINNER")
            lines.append(f"   Calories: {dinner['calories']:.0f} ({dinner_pct:.0f}%) | Protein: {dinner['protein_g']:.1f}g")
            for item in dinner["foods"]:
                food_name = self.calc.get_food_name(item["food"])
                lines.append(f"   • {food_name}: {item['quantity_g']}g")
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def print_plan(self, plan: List[Dict], totals: Dict) -> None:
        """Print a formatted meal plan."""
        print(self.format_plan(plan, totals))
    
    def print_plan_with_meals(self, meals: Dict, totals: Dict) -> None:
        """Print meal plan with distribution across meals."""
        print(self.format_plan_with_meals(meals, totals))
    
    def format_quick_summary(self, totals: Dict) -> str:
        """
        Format a quick one-line summary.
        
        Returns:
            String like "Protein: 152g | Calories: 2850 | Carbs: 320g | Fat: 80g"
        """
        return (f"Protein: {totals['total_protein_g']:.0f}g | "
                f"Calories: {totals['total_calories']:.0f} kcal | "
                f"Carbs: {totals['total_carb_g']:.0f}g | "
                f"Fat: {totals['total_fat_g']:.0f}g")
