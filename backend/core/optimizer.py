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
    
    # Optimization modes with weighted scoring factors
    MODES = {
        "cheapest": {
            "cost_weight": 0.70,
            "protein_weight": 0.15,
            "variety_weight": 0.05,
            "quality_weight": 0.10,
            "description": "Minimize cost (maximum savings)"
        },
        "balanced": {
            "cost_weight": 0.30,
            "protein_weight": 0.25,
            "variety_weight": 0.25,
            "quality_weight": 0.20,
            "description": "Balance cost vs nutrition"
        },
        "premium": {
            "cost_weight": 0.10,
            "protein_weight": 0.25,
            "variety_weight": 0.25,
            "quality_weight": 0.40,
            "description": "Maximize nutrition quality (higher cost)"
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
        Generate nutritionally valid + cost-optimized meal plan FOR A SPECIFIC BUDGET MODE.
        
        Different modes get different food selection strategies:
        - CHEAPEST: Strongly prefer cheap foods (rice, bread, lentil)
        - BALANCED: Mix of cost and quality
        - PREMIUM: Prefer high-quality proteins (chicken, fish, eggs)
        
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
        
        # STRATEGY: For each mode, generate multiple diverse candidates, then score
        # but with MODE-SPECIFIC food preferences built in
        
        candidates = self._generate_mode_specific_candidates(
            target_calories,
            target_protein_g,
            target_fat_g,
            target_carb_g,
            tolerance_calories,
            tolerance_protein,
            budget_mode,
            enforce_variety
        )
        
        if not candidates:
            print(f"ERROR: No valid candidate plans found for {budget_mode} mode")
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
    
    def _generate_mode_specific_candidates(self,
                                          target_calories: float,
                                          target_protein_g: float,
                                          target_fat_g: float,
                                          target_carb_g: float,
                                          tolerance_calories: float,
                                          tolerance_protein: float,
                                          budget_mode: str,
                                          enforce_variety: bool) -> List[List[Dict]]:
        """
        Generate MODE-SPECIFIC candidates by adjusting macronutrient targets.
        
        Different modes emphasize different nutrients:
        - CHEAPEST: Lower protein, more carbs -> forces budget-friendly legumes and rice
        - BALANCED: Standard targets -> balanced mix of proteins and carbs
        - PREMIUM: Higher protein, more fat, lower carbs -> forces high-quality proteins (meats, fish)
        """
        candidates = []
        
        if budget_mode == "cheapest":
            # Cheapest: Lower protein demand (100g instead of 120g)
            # This allows planner to use more rice/bread instead of expensive proteins
            for max_foods in [3, 4, 5]:
                plan = self.planner.generate_plan(
                    target_calories=target_calories,
                    target_protein_g=max(target_protein_g * 0.85, 80),  # 15% lower
                    target_fat_g=target_fat_g * 0.8 if target_fat_g else None,  # Lower fat
                    target_carb_g=target_carb_g * 1.1 if target_carb_g else None,  # Higher carbs
                    tolerance_calories=tolerance_calories,
                    tolerance_protein=tolerance_protein,
                    enforce_variety=False,  # Allow repetition for cheaper combinations
                    max_foods=max_foods
                )
                if plan:
                    candidates.append(plan)
        
        elif budget_mode == "premium":
            # Premium: Higher protein demand (140g+ instead of 120g)
            # This forces planner to include expensive high-quality proteins
            for max_foods in [4, 5, 6]:
                plan = self.planner.generate_plan(
                    target_calories=target_calories,
                    target_protein_g=target_protein_g * 1.15,  # 15% higher
                    target_fat_g=target_fat_g * 1.3 if target_fat_g else None,  # More fat (meats)
                    target_carb_g=target_carb_g * 0.85 if target_carb_g else None,  # Lower carbs
                    tolerance_calories=tolerance_calories,
                    tolerance_protein=tolerance_protein,
                    enforce_variety=True,  # Enforce variety for quality
                    max_foods=max_foods
                )
                if plan:
                    candidates.append(plan)
        
        else:  # balanced
            # Balanced: Standard targets
            for max_foods in [3, 4, 5]:
                plan = self.planner.generate_plan(
                    target_calories=target_calories,
                    target_protein_g=target_protein_g,
                    target_fat_g=target_fat_g,
                    target_carb_g=target_carb_g,
                    tolerance_calories=tolerance_calories,
                    tolerance_protein=tolerance_protein,
                    enforce_variety=enforce_variety,
                    max_foods=max_foods
                )
                if plan:
                    candidates.append(plan)
        
        # If we don't have enough candidates, try again with relaxed constraints
        if len(candidates) < 2:
            plan = self.planner.generate_plan(
                target_calories=target_calories,
                target_protein_g=target_protein_g,
                target_fat_g=target_fat_g,
                target_carb_g=target_carb_g,
                tolerance_calories=tolerance_calories * 2,
                tolerance_protein=tolerance_protein * 2,
                enforce_variety=False,
                max_foods=6
            )
            if plan:
                candidates.append(plan)
        
        # Remove duplicates
        unique_candidates = []
        for plan in candidates:
            foods_in_plan = sorted([item["food"] for item in plan])
            is_duplicate = False
            for existing in unique_candidates:
                existing_foods = sorted([item["food"] for item in existing])
                if foods_in_plan == existing_foods:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_candidates.append(plan)
        
        return unique_candidates
    
    def _score_plans(self,
                    plans: List[List[Dict]],
                    budget_mode: str,
                    target_protein_g: float,
                    target_calories: float) -> List[Tuple]:
        """
        Score candidate plans based on budget mode with weighted factors.
        
        Weighted scoring:
        - CHEAPEST: Emphasize cost (70%), minimal quality (10%)
        - BALANCED: Equal weight cost/variety/quality (30%/25%/20%)
        - PREMIUM: Emphasize quality (40%), cost lower priority (10%)
        
        Returns:
            List of (plan, score, metrics) tuples, sorted by score (highest first)
        """
        scored = []
        
        mode_config = self.MODES[budget_mode]
        cost_weight = mode_config["cost_weight"]
        protein_weight = mode_config["protein_weight"]
        variety_weight = mode_config["variety_weight"]
        quality_weight = mode_config["quality_weight"]
        
        daily_costs = [self.cc.calculate_daily_cost(p) for p in plans]
        min_cost = min(daily_costs) if daily_costs else 1
        max_cost = max(daily_costs) if daily_costs else 1
        cost_range = max(max_cost - min_cost, 1)
        
        for plan, daily_cost in zip(plans, daily_costs):
            
            cost_score = 1.0 - ((daily_cost - min_cost) / cost_range)
            # ─── Calculate component scores ───────────────────────────────────
            
            # 1. COST SCORE (lower cost = higher score)
            # daily_cost = self.cc.calculate_daily_cost(plan)
            # Normalize: assume typical plan costs 100-250 BDT
            # cost_normalized = min(daily_cost / 250, 1.0)
            # cost_score = 1.0 - cost_normalized  # Invert: lower cost = higher score
            
            # 2. PROTEIN SCORE (how close to target)
            total_protein = sum(item.get("protein_g", 0) for item in plan)
            protein_diff = abs(total_protein - target_protein_g) / target_protein_g if target_protein_g > 0 else 0
            protein_score = max(0, 1.0 - protein_diff)
            
            # 3. CALORIE SCORE (how close to target)
            total_calories = sum(item.get("calories", 0) for item in plan)
            calorie_diff = abs(total_calories - target_calories) / target_calories if target_calories > 0 else 0
            calorie_score = max(0, 1.0 - calorie_diff)
            
            # 4. VARIETY SCORE (number of different foods + category diversity)
            num_foods = len(plan)
            variety_score = min(num_foods / 5, 1.0)  # Max 5 foods = perfect variety
            
            # Check category diversity
            categories = set([item.get("category", "other") for item in plan])
            category_diversity = len(categories) / 5  # Max 5 categories possible
            variety_score = (variety_score + category_diversity) / 2
            
            # 5. QUALITY SCORE (average protein quality of foods in plan)
            quality_scores = []
            for item in plan:
                food_key = item["food"]
                if food_key in self.calc.food_data:
                    protein_quality = self.calc.food_data[food_key].get("protein_quality", 5) / 10
                    quality_scores.append(protein_quality)
            
            quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5
            
            # ─── Combine scores based on mode weights ───────────────────────────────
            
            # Macro nutrition score (average of protein + calorie accuracy)
            macro_score = (protein_score + calorie_score) / 2
            
            # Combined score with mode-specific weights
            combined_score = (
                (cost_weight * cost_score) +
                (protein_weight * macro_score) +
                (variety_weight * variety_score) +
                (quality_weight * quality_score)
            )
            
            metrics = {
                "daily_cost_bdt": daily_cost,
                "monthly_cost_bdt": self.cc.calculate_monthly_cost(plan),
                "total_protein_g": total_protein,
                "total_calories": total_calories,
                "protein_per_taka": self.cc.calculate_protein_per_taka(plan),
                "protein_per_100_taka": self.cc.calculate_protein_per_100_taka(plan),
                "calories_per_100_taka": self.cc.calculate_calories_per_taka(plan) * 100,
                "num_foods": num_foods,
                "avg_protein_quality": round(quality_score * 10, 1),
                "variety_score": round(variety_score, 3),
                "cost_score": round(cost_score, 3),
                "protein_score": round(macro_score, 3),
                "quality_score": round(quality_score, 3),
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
                enforce_variety=False
            )
            
            if plan:
                results[mode] = (plan, metrics)
            
            else:
                print(f"Warning: Mode {mode} produced no plan -- skipping")
        
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
