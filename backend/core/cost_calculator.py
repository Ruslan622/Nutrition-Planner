"""
Cost Calculator v1
Calculates daily/monthly costs and cost efficiency metrics.
Core metric: protein_per_taka (protein per BDT spent) — used for plan comparison.
"""

from typing import List, Dict


class CostCalculator:
    """Calculate costs and efficiency metrics for meal plans."""
    
    def __init__(self, price_manager):
        """
        Initialize cost calculator with a PriceManager instance.
        
        Args:
            price_manager: PriceManager instance with normalized prices
        """
        self.pm = price_manager
    
    def calculate_plan_cost(self, plan: List[Dict]) -> Dict:
        """
        Calculate total cost and cost metrics for a meal plan.
        
        Args:
            plan: List of meal items from MealPlanner.generate_plan()
                  Each item must have 'food' and 'quantity_g' keys
            
        Returns:
            Dict with:
            - total_cost_bdt: Total daily cost in BDT
            - cost_per_item: List of (food, quantity_g, cost) tuples
            - cost_breakdown: Dict of food → cost
        """
        total_cost = 0
        cost_per_item = []
        cost_breakdown = {}
        
        for item in plan:
            food_key = item["food"]
            quantity_g = item["quantity_g"]
            
            # Calculate cost for this item
            cost = self.pm.get_price_for_quantity(food_key, quantity_g)
            total_cost += cost
            
            cost_per_item.append({
                "food": food_key,
                "quantity_g": quantity_g,
                "cost_bdt": cost
            })
            
            # Accumulate cost by food
            if food_key not in cost_breakdown:
                cost_breakdown[food_key] = 0
            cost_breakdown[food_key] += cost
        
        return {
            "total_cost_bdt": round(total_cost, 2),
            "cost_per_item": cost_per_item,
            "cost_breakdown": cost_breakdown,
        }
    
    def calculate_daily_cost(self, plan: List[Dict]) -> float:
        """Calculate total daily cost in BDT."""
        cost_info = self.calculate_plan_cost(plan)
        return cost_info["total_cost_bdt"]
    
    def calculate_monthly_cost(self, plan: List[Dict], days: int = 30) -> float:
        """Calculate monthly cost (daily cost × 30 days)."""
        daily_cost = self.calculate_daily_cost(plan)
        return round(daily_cost * days, 2)
    
    def calculate_cost_per_macro(self, plan: List[Dict], macro: str) -> float:
        """
        Calculate cost per unit of macro (protein, carbs, fat, calories).
        
        Args:
            plan: Meal plan
            macro: One of "protein", "carbs", "fat", "calories"
            
        Returns:
            Cost per unit of macro (BDT/g for protein/carbs/fat, BDT/kcal for calories)
        """
        total_cost = self.calculate_daily_cost(plan)
        
        # Calculate total macros
        total_macro = sum(item.get(f"{macro}_g", item.get(f"{macro}", 0)) for item in plan)
        
        if total_macro <= 0:
            return 0
        
        return round(total_cost / total_macro, 3)
    
    def calculate_protein_per_taka(self, plan: List[Dict]) -> float:
        """
        PRIMARY EFFICIENCY METRIC: Protein per Taka spent.
        
        Args:
            plan: Meal plan
            
        Returns:
            Grams of protein per 1 BDT spent (g/BDT)
        """
        total_cost = self.calculate_daily_cost(plan)
        
        # Calculate total protein
        total_protein = sum(item.get("protein_g", 0) for item in plan)
        
        if total_cost <= 0:
            return 0
        
        return round(total_protein / total_cost, 3)
    
    def calculate_protein_per_100_taka(self, plan: List[Dict]) -> float:
        """Convenience metric: grams of protein per 100 BDT spent."""
        return round(self.calculate_protein_per_taka(plan) * 100, 2)
    
    def calculate_calories_per_taka(self, plan: List[Dict]) -> float:
        """
        Calorie efficiency: Calories per Taka spent (kcal/BDT).
        
        Args:
            plan: Meal plan
            
        Returns:
            Calories per 1 BDT spent
        """
        total_cost = self.calculate_daily_cost(plan)
        
        # Calculate total calories
        total_calories = sum(item.get("calories", 0) for item in plan)
        
        if total_cost <= 0:
            return 0
        
        return round(total_calories / total_cost, 3)
    
    def calculate_cost_per_1000cal(self, plan: List[Dict]) -> float:
        """Cost to get 1000 kcal."""
        calories_per_taka = self.calculate_calories_per_taka(plan)
        if calories_per_taka <= 0:
            return 0
        return round(1000 / calories_per_taka, 2)
    
    def compare_plans(self, plans: List[List[Dict]]) -> List[Dict]:
        """
        Compare multiple meal plans on cost and efficiency metrics.
        
        Args:
            plans: List of meal plans to compare
            
        Returns:
            List of dicts with comparison metrics for each plan
        """
        comparison = []
        
        for i, plan in enumerate(plans):
            cost_info = self.calculate_plan_cost(plan)
            total_calories = sum(item.get("calories", 0) for item in plan)
            total_protein = sum(item.get("protein_g", 0) for item in plan)
            
            comparison.append({
                "plan_id": i,
                "daily_cost_bdt": cost_info["total_cost_bdt"],
                "monthly_cost_bdt": self.calculate_monthly_cost(plan),
                "total_calories": total_calories,
                "total_protein_g": total_protein,
                "protein_per_taka": self.calculate_protein_per_taka(plan),
                "calories_per_taka": self.calculate_calories_per_taka(plan),
                "cost_per_1000cal": self.calculate_cost_per_1000cal(plan),
                "num_foods": len(plan),
            })
        
        return comparison
    
    def print_cost_analysis(self, plan: List[Dict], totals: Dict = None) -> str:
        """
        Format cost analysis for display.
        
        Args:
            plan: Meal plan
            totals: Optional nutritional totals dict
            
        Returns:
            Formatted string
        """
        cost_info = self.calculate_plan_cost(plan)
        
        lines = []
        lines.append("\n" + "="*70)
        lines.append("COST ANALYSIS")
        lines.append("="*70)
        
        lines.append(f"\nDaily Cost: {cost_info['total_cost_bdt']:.2f} BDT")
        lines.append(f"Monthly Cost: {self.calculate_monthly_cost(plan):.2f} BDT (30 days)")
        
        if totals:
            protein_per_taka = self.calculate_protein_per_taka(plan)
            calories_per_taka = self.calculate_calories_per_taka(plan)
            
            lines.append(f"\n[EFFICIENCY METRICS]")
            lines.append(f"Protein per 100 BDT: {self.calculate_protein_per_100_taka(plan):.1f}g")
            lines.append(f"Calories per 100 BDT: {calories_per_taka * 100:.0f} kcal")
            lines.append(f"Cost per 1000 kcal: {self.calculate_cost_per_1000cal(plan):.2f} BDT")
        
        lines.append(f"\n[COST BREAKDOWN]")
        for food_key, cost in sorted(cost_info["cost_breakdown"].items(), key=lambda x: x[1], reverse=True):
            pct = (cost / cost_info["total_cost_bdt"]) * 100 if cost_info["total_cost_bdt"] > 0 else 0
            lines.append(f"  {food_key:12} {cost:8.2f} BDT ({pct:5.1f}%)")
        
        lines.append("="*70)
        
        return "\n".join(lines)
