"""
Optimizer v1 — THE BRAIN
Combines nutrition + prices to generate cost-optimized meal plans.
Core responsibility: minimize cost while preserving nutritional targets.

Budget modes:
- CHEAPEST: Minimize cost (maximum savings)
- BALANCED: Balance cost vs nutrition quality
- PREMIUM: Maximize nutrition quality (allow higher cost)
"""

from typing import List, Dict, Tuple
from itertools import combinations


class Optimizer:
    """
    Multi-objective optimizer for cost-aware meal plans.
    
    Combines:
    1. Nutritional constraints (macros, variety, distribution)
    2. Price efficiency (protein per taka)
    3. Budget modes (cheapest, balanced, premium)
    """
    
    # Optimization modes
    MODES = {
        "cheapest": {
            "cost_weight": 1.0,
            "nutrition_weight": 0.5,
            "description": "Minimize cost (maximum savings)"
        },
        "balanced": {
            "cost_weight": 0.6,
            "nutrition_weight": 0.9,
            "description": "Balance cost vs nutrition"
        },
        "premium": {
            "cost_weight": 0.2,
            "nutrition_weight": 1.0,
            "description": "Maximize nutrition quality"
        },
    }
    
    def __init__(self, calculator, planner, price_manager, cost_calculator):
        """
        Initialize optimizer with all required components.
        
        Args:
            calculator: NutritionCalculator instance
            planner: MealPlanner instance
            price_manager: PriceManager instance
            cost_calculator: CostCalculator instance
        """
        self.calc = calculator
        self.planner = planner
        self.pm = price_manager
        self.cc = cost_calculator
    
    def generate_optimized_plan(self,
                               target_calories: float,
                               target_protein_g: float,
                               target_fat_g: float = None,
                               target_carb_g: float = None,
                               tolerance_calories: float = 100,
                               tolerance_protein: float = 5,
                               budget_mode: str = "balanced",
                               max_budget_bdt: float = None,
                               enforce_variety: bool = True) -> Tuple[List[Dict], Dict]:
        """
        Generate nutritionally valid + cost-optimized meal plan.
        
        Args:
            target_calories: Target calories
            target_protein_g: Target protein
            target_fat_g: Target fat (optional)
            target_carb_g: Target carbs (optional)
            tolerance_calories: ±tolerance around targets
            tolerance_protein: ±tolerance around targets
            budget_mode: "cheapest", "balanced", or "premium"
            max_budget_bdt: Hard cap on daily budget (optional)
            enforce_variety: Enforce food variety constraints
            
        Returns:
            Tuple (optimized_plan, optimization_metrics)
        """
        
        if budget_mode not in self.MODES:
            print(f"WARNING: Unknown budget mode '{budget_mode}', using 'balanced'")
            budget_mode = "balanced"
        
        # Get candidate plans (nutritionally valid)
        candidates = self._generate_candidate_plans(
            target_calories,
            target_protein_g,
            target_fat_g,
            target_carb_g,
            tolerance_calories,
            tolerance_protein,
            enforce_variety
        )
        
        if not candidates:
            print("ERROR: No valid candidate plans found")
            return [], {}
        
        # Filter by budget if specified
        if max_budget_bdt:
            candidates = [
                plan for plan in candidates
                if self.cc.calculate_daily_cost(plan) <= max_budget_bdt
            ]
            
            if not candidates:
                print(f"ERROR: No plans within budget of {max_budget_bdt} BDT")
                return [], {}
        
        # Score and rank candidates
        scored_plans = self._score_plans(candidates, budget_mode, target_protein_g, target_calories)
        
        if not scored_plans:
            return [], {}
        
        # Best plan is first (highest score)
        best_plan, best_score, metrics = scored_plans[0]
        
        return best_plan, metrics
    
    def _generate_candidate_plans(self,
                                  target_calories: float,
                                  target_protein_g: float,
                                  target_fat_g: float,
                                  target_carb_g: float,
                                  tolerance_calories: float,
                                  tolerance_protein: float,
                                  enforce_variety: bool) -> List[List[Dict]]:
        """
        Generate multiple nutritionally valid candidate plans.
        These will be scored and ranked by cost.
        
        Returns:
            List of candidate plans
        """
        candidates = []
        
        # Generate base plan
        base_plan = self.planner.generate_plan(
            target_calories=target_calories,
            target_protein_g=target_protein_g,
            target_fat_g=target_fat_g,
            target_carb_g=target_carb_g,
            tolerance_calories=tolerance_calories,
            tolerance_protein=tolerance_protein,
            enforce_variety=enforce_variety,
            max_foods=6
        )
        
        if base_plan:
            candidates.append(base_plan)
        
        # Try with different max_foods to get variations
        for max_foods in [4, 5]:
            alt_plan = self.planner.generate_plan(
                target_calories=target_calories,
                target_protein_g=target_protein_g,
                target_fat_g=target_fat_g,
                target_carb_g=target_carb_g,
                tolerance_calories=tolerance_calories,
                tolerance_protein=tolerance_protein,
                enforce_variety=enforce_variety,
                max_foods=max_foods
            )
            if alt_plan:
                # Check if this is a new plan (not in candidates)
                is_new = True
                for existing in candidates:
                    if len(alt_plan) == len(existing):
                        foods_match = all(
                            alt_plan[i]["food"] == existing[i]["food"]
                            for i in range(len(alt_plan))
                        )
                        if foods_match:
                            is_new = False
                            break
                
                if is_new:
                    candidates.append(alt_plan)
        
        # If still no candidates, try with relaxed tolerances
        if not candidates:
            relaxed_plan = self.planner.generate_plan(
                target_calories=target_calories,
                target_protein_g=target_protein_g,
                target_fat_g=target_fat_g,
                target_carb_g=target_carb_g,
                tolerance_calories=tolerance_calories * 1.5,
                tolerance_protein=tolerance_protein * 1.5,
                enforce_variety=enforce_variety,
                max_foods=6
            )
            if relaxed_plan:
                candidates.append(relaxed_plan)
        
        return candidates
    
    def _score_plans(self,
                    plans: List[List[Dict]],
                    budget_mode: str,
                    target_protein_g: float,
                    target_calories: float) -> List[Tuple]:
        """
        Score candidate plans based on budget mode.
        
        Returns:
            List of (plan, score, metrics) tuples, sorted by score (highest first)
        """
        scored = []
        
        mode_config = self.MODES[budget_mode]
        cost_weight = mode_config["cost_weight"]
        nutrition_weight = mode_config["nutrition_weight"]
        
        for plan in plans:
            # Calculate metrics
            daily_cost = self.cc.calculate_daily_cost(plan)
            total_protein = sum(item.get("protein_g", 0) for item in plan)
            total_calories = sum(item.get("calories", 0) for item in plan)
            protein_per_taka = self.cc.calculate_protein_per_taka(plan)
            
            # Normalize metrics to [0, 1] for scoring
            # Lower cost is better → normalize inversely
            cost_score = 1.0 / (1.0 + daily_cost / 500)  # Sigmoid-like normalization
            
            # Protein accuracy: how close to target?
            protein_error = abs(total_protein - target_protein_g) / target_protein_g if target_protein_g > 0 else 0
            protein_score = max(0, 1.0 - protein_error)
            
            # Calorie accuracy: how close to target?
            calorie_error = abs(total_calories - target_calories) / target_calories if target_calories > 0 else 0
            calorie_score = max(0, 1.0 - calorie_error)
            
            nutrition_score = (protein_score + calorie_score) / 2
            
            # Combined score based on mode
            # More weight on cost in "cheapest", more on nutrition in "premium"
            combined_score = (cost_weight * cost_score) + (nutrition_weight * nutrition_score)
            
            metrics = {
                "daily_cost_bdt": daily_cost,
                "monthly_cost_bdt": self.cc.calculate_monthly_cost(plan),
                "total_protein_g": total_protein,
                "total_calories": total_calories,
                "protein_per_taka": protein_per_taka,
                "protein_per_100_taka": self.cc.calculate_protein_per_100_taka(plan),
                "calories_per_100_taka": self.cc.calculate_calories_per_taka(plan) * 100,
                "cost_score": round(cost_score, 3),
                "nutrition_score": round(nutrition_score, 3),
                "combined_score": round(combined_score, 3),
                "budget_mode": budget_mode,
            }
            
            scored.append((plan, combined_score, metrics))
        
        # Sort by score (highest first)
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored
    
    def generate_plans_all_modes(self,
                                target_calories: float,
                                target_protein_g: float,
                                target_fat_g: float = None,
                                target_carb_g: float = None,
                                tolerance_calories: float = 100,
                                tolerance_protein: float = 5) -> Dict[str, Tuple]:
        """
        Generate optimized plans for all budget modes at once.
        Allows user to compare cheapest vs balanced vs premium options.
        
        Returns:
            Dict mapping mode_name → (plan, metrics)
        """
        results = {}
        
        for mode in self.MODES.keys():
            plan, metrics = self.generate_optimized_plan(
                target_calories=target_calories,
                target_protein_g=target_protein_g,
                target_fat_g=target_fat_g,
                target_carb_g=target_carb_g,
                tolerance_calories=tolerance_calories,
                tolerance_protein=tolerance_protein,
                budget_mode=mode,
                enforce_variety=True
            )
            
            if plan:
                results[mode] = (plan, metrics)
        
        return results
    
    def print_optimization_summary(self, plans_by_mode: Dict[str, Tuple]) -> str:
        """
        Print comparison of all budget modes.
        
        Args:
            plans_by_mode: Output from generate_plans_all_modes()
            
        Returns:
            Formatted comparison string
        """
        lines = []
        lines.append("\n" + "="*80)
        lines.append("COST-OPTIMIZED PLANS — BUDGET MODE COMPARISON")
        lines.append("="*80)
        
        # Header
        lines.append(f"{'Mode':<12} {'Daily Cost':<12} {'Protein/Taka':<14} {'Protein':<10} {'Calories':<10}")
        lines.append("-"*80)
        
        # Data rows
        for mode in ["cheapest", "balanced", "premium"]:
            if mode in plans_by_mode:
                plan, metrics = plans_by_mode[mode]
                mode_label = mode.upper()
                cost = metrics["daily_cost_bdt"]
                ppt = metrics["protein_per_100_taka"]
                protein = metrics["total_protein_g"]
                calories = metrics["total_calories"]
                
                lines.append(f"{mode_label:<12} {cost:>10.2f} BDT  {ppt:>10.1f}g       {protein:>8.0f}g    {calories:>8.0f} kcal")
        
        lines.append("="*80 + "\n")
        
        return "\n".join(lines)
