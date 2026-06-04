"""
MealPlanner v2
Generates realistic meal plans with:
- Serving constraints (min/max per food)
- Variety rules (at least 1 protein + 1 carb source)
- No food dominance (max 40% daily calories)
- Meal distribution (breakfast/lunch/dinner)
- Advanced scoring algorithm
"""

from typing import List, Dict, Tuple
from itertools import combinations


class MealPlanner:
    """Generate meal plans with realistic constraints."""
    
    # Hard constraints for meal distribution
    MEAL_DISTRIBUTION = {
        "breakfast": {"min_pct": 0.15, "max_pct": 0.30, "target_pct": 0.25},
        "lunch": {"min_pct": 0.30, "max_pct": 0.45, "target_pct": 0.40},
        "dinner": {"min_pct": 0.25, "max_pct": 0.45, "target_pct": 0.35},
    }
    
    def __init__(self, calculator):
        """Initialize planner with a NutritionCalculator instance."""
        self.calc = calculator
    
    def generate_plan(self,
                      target_calories: float,
                      target_protein_g: float,
                      target_fat_g: float = None,
                      target_carb_g: float = None,
                      tolerance_calories: float = 100,
                      tolerance_protein: float = 5,
                      max_foods: int = 6,
                      enforce_variety: bool = True) -> List[Dict]:
        """
        Generate a realistic meal plan with constraints and scoring.
        
        Args:
            target_calories: Target calories for the day
            target_protein_g: Target protein in grams
            target_fat_g: Target fat in grams (optional)
            target_carb_g: Target carbs in grams (optional)
            tolerance_calories: ±tolerance around target_calories
            tolerance_protein: ±tolerance around target_protein_g
            max_foods: Maximum foods in the plan
            enforce_variety: Enforce at least 1 protein + 1 carb source
            
        Returns:
            List of dicts with best-scored meal plan
        """
        # Use constraint-aware greedy algorithm
        plan = self._greedy_with_constraints(
            target_calories,
            target_protein_g,
            target_fat_g,
            target_carb_g,
            tolerance_calories,
            tolerance_protein,
            max_foods,
            enforce_variety
        )
        
        if plan:
            # Round to serving sizes
            return self._apply_serving_granularity(plan)
        
        # Fallback: brute force with constraints
        plan = self._brute_force_with_constraints(
            target_calories,
            target_protein_g,
            target_fat_g,
            target_carb_g,
            tolerance_calories,
            tolerance_protein,
            max_foods,
            enforce_variety
        )
        
        if plan:
            return self._apply_serving_granularity(plan)
        
        return []
    
    def _greedy_with_constraints(self,
                                 target_calories: float,
                                 target_protein_g: float,
                                 target_fat_g: float,
                                 target_carb_g: float,
                                 tolerance_calories: float,
                                 tolerance_protein: float,
                                 max_foods: int,
                                 enforce_variety: bool) -> List[Dict]:
        """
        Greedy algorithm that respects serving constraints and variety rules.
        """
        plan = []
        current_calories = 0
        current_protein = 0
        categories_covered = set()
        
        # Get foods sorted by protein density
        foods = self.calc.available_foods()
        
        
        
        carb_seeds = [f for f in ["rice", "bread"] if f in foods]
        for seed in carb_seeds:
            macros_100 = self.calc.get_food_macros(seed, 100)
            base_qty = min(300, macros_100.get("max_serving_g", 300))
            macros = self.calc.get_food_macros(seed, base_qty)
            if macros["calories"] / target_calories <= 0.40:
                plan.append({
                "food": seed,
                "quantity_g": base_qty,
                "calories": macros["calories"],
                "protein_g": macros["protein_g"],
                "fat_g": macros["fat_g"],
                "carb_g": macros["carb_g"],
                "fiber_g": macros["fiber_g"],
                "iron_mg": macros.get("iron_mg", 0),
                "calcium_mg": macros.get("calcium_mg", 0),
                "vitamin_d_mcg": macros.get("vitamin_d_mcg", 0),
                "vitamin_c_mg": macros.get("vitamin_c_mg", 0),
                "potassium_mg": macros.get("potassium_mg", 0),
                "category": macros_100.get("category", "carb"),
            })
                current_calories += macros["calories"]
                current_protein += macros["protein_g"]
                categories_covered.add(macros_100.get("category", "carb"))
                break  # one carb seed is enough
        food_scores = {}
        for food_key in foods:
            macros = self.calc.get_food_macros(food_key, 100)
            # Score: protein/calorie ratio (higher = more efficient)
            score = (macros["protein_g"] / macros["calories"] 
                    if macros["calories"] > 0 else 0)
            food_scores[food_key] = score
        
        sorted_foods = sorted(food_scores.items(), key=lambda x: x[1], reverse=True)
        
        for food_key, _ in sorted_foods:
            if len(plan) >= max_foods:
                break
            
            macros_100 = self.calc.get_food_macros(food_key, 100)
            min_qty = macros_100.get("min_serving_g", 50)
            max_qty = macros_100.get("max_serving_g", 500)
            category = macros_100.get("category", "other")
            
            # Skip if food already in plan and would exceed max
            if any(item["food"] == food_key for item in plan):
                continue
            
            # Calculate remaining needs
            calories_needed = target_calories - current_calories
            protein_needed = target_protein_g - current_protein

            # Skip if targets met
            if (abs(calories_needed) <= tolerance_calories and
                abs(protein_needed) <= tolerance_protein * 3):
                break

            cal_per_100 = max(macros_100.get("calories", 1), 1)
            pro_per_100 = max(macros_100.get("protein_g", 0.1), 0.1)

            # Cap quantity by remaining calories
            if calories_needed > 0:
                max_by_calories = int((calories_needed / (cal_per_100 / 100)) * 1.3)
            else:
                max_by_calories = min_qty

            # Cap quantity by remaining protein budget
            if protein_needed > 0:
                max_by_protein = int((protein_needed / (pro_per_100 / 100)) * 1.2)
            else:
                max_by_protein = min_qty

            # Use the more restrictive cap
            dynamic_max = min(max_by_calories, max_by_protein)
            max_qty = max(min_qty + 50, min(800, dynamic_max))
            
            # Find best quantity that respects constraints
            best_quantity = None
            best_score = float('inf')
            
            for quantity_g in range(min_qty, max_qty + 1, 50):
                macros = self.calc.get_food_macros(food_key, quantity_g)
                test_calories = current_calories + macros["calories"]
                test_protein = current_protein + macros["protein_g"]
                
                # Check dominance constraint (max 40% daily calories per food)
                food_calorie_pct = macros["calories"] / target_calories
                if food_calorie_pct > 0.40:
                    continue
                
                # Calculate distance to targets
                cal_distance = abs(test_calories - target_calories)

                # Penalize overshoot much harder than undershoot
                pro_over = max(0, test_protein - target_protein_g)
                pro_under = max(0, target_protein_g - test_protein)
                pro_distance = (pro_over * 3.0) + (pro_under * 0.5)

                score = cal_distance + pro_distance
                
                if score < best_score:
                    best_score = score
                    best_quantity = quantity_g
            
            if best_quantity:
                macros = self.calc.get_food_macros(food_key, best_quantity)
                plan.append({
                    "food": food_key,
                    "quantity_g": best_quantity,
                    "calories": macros["calories"],
                    "protein_g": macros["protein_g"],
                    "fat_g": macros["fat_g"],
                    "carb_g": macros["carb_g"],
                    "fiber_g": macros["fiber_g"],
                    "iron_mg": macros.get("iron_mg", 0),
                    "calcium_mg": macros.get("calcium_mg", 0),
                    "vitamin_d_mcg": macros.get("vitamin_d_mcg", 0),
                    "vitamin_c_mg": macros.get("vitamin_c_mg", 0),
                    "potassium_mg": macros.get("potassium_mg", 0),
                    "category": category,
                })
                current_calories += macros["calories"]
                current_protein += macros["protein_g"]
                categories_covered.add(category)
        
        # Validate: check variety and targets
        cal_diff = abs(current_calories - target_calories)
        pro_diff = abs(current_protein - target_protein_g)
        
        if cal_diff <= tolerance_calories and pro_diff <= tolerance_protein:
            # Check variety if enforced
            if not enforce_variety or self._check_variety(plan):
                return plan
            
        print(f"DEBUG greedy: cal_diff={cal_diff:.1f} tol={tolerance_calories:.1f} | pro_diff={pro_diff:.1f} tol={tolerance_protein:.1f} | foods={[i['food'] for i in plan]} | total_cal={current_calories:.0f}")
        return []
    
    def _brute_force_with_constraints(self,
                                     target_calories: float,
                                     target_protein_g: float,
                                     target_fat_g: float,
                                     target_carb_g: float,
                                     tolerance_calories: float,
                                     tolerance_protein: float,
                                     max_foods: int,
                                     enforce_variety: bool) -> List[Dict]:
        """Brute force search respecting all constraints."""
        foods = self.calc.available_foods()
        
        for num_foods in range(1, min(5, max_foods + 1)):
            for food_combo in combinations(foods, num_foods):
                iterations = max(12, int(target_calories / 200))
                for quantities in self._generate_quantity_combinations(food_combo, num_foods, iterations):
                    plan = []
                    total_cals = 0
                    total_protein = 0
                    valid = True
                    
                    for food_key, qty in zip(food_combo, quantities):
                        food_cfg = self.calc.get_food_macros(food_key, 100)  # config dict has constraints
                        min_qty = food_cfg.get("min_serving_g", 50)
                        max_qty = food_cfg.get("max_serving_g", 500)
                        macros = self.calc.get_food_macros(food_key, qty)
                        if not (min_qty <= qty <= max_qty):
                            valid = False
                            break
                        
                        # Check dominance constraint
                        food_pct = macros["calories"] / target_calories
                        if food_pct > 0.40:
                            valid = False
                            break
                        
                        plan.append({
                            "food": food_key,
                            "quantity_g": qty,
                            "calories": macros["calories"],
                            "protein_g": macros["protein_g"],
                            "fat_g": macros["fat_g"],
                            "carb_g": macros["carb_g"],
                            "fiber_g": macros["fiber_g"],
                            "iron_mg": macros.get("iron_mg", 0),
                            "calcium_mg": macros.get("calcium_mg", 0),
                            "vitamin_d_mcg": macros.get("vitamin_d_mcg", 0),
                            "vitamin_c_mg": macros.get("vitamin_c_mg", 0),
                            "potassium_mg": macros.get("potassium_mg", 0),
                            "category": macros.get("category", "other"),
                        })
                        total_cals += macros["calories"]
                        total_protein += macros["protein_g"]
                    
                    if not valid:
                        continue
                    
                    # Check targets
                    if (abs(total_cals - target_calories) <= tolerance_calories and
                        abs(total_protein - target_protein_g) <= tolerance_protein):
                        
                        # Check variety
                        if not enforce_variety or self._check_variety(plan):
                            return plan
        
        return []
    
    def _check_variety(self, plan: List[Dict]) -> bool:
        """
        Check if plan has minimum variety:
        - At least 1 protein source
        - At least 1 carb source
        - Not more than 2 dominant foods (>35% of calories each)
        """
        categories = set()
        for item in plan:
            categories.add(item.get("category", "other"))
        
        # Need at least one protein-like and one carb-like
        has_protein = any(cat in ["protein", "protein_carb"] 
                         for cat in categories)
        has_carb = any(cat in ["carb", "protein_carb"] 
                      for cat in categories)
        
        if not (has_protein and has_carb):
            return False
        
        # Count dominant foods
        total_cals = sum(item["calories"] for item in plan)
        dominant_count = 0
        for item in plan:
            if item["calories"] / total_cals > 0.35:
                dominant_count += 1
        
        return dominant_count <= 2
    
    def _generate_quantity_combinations(self, 
                                       food_combo: Tuple,
                                       num_foods: int,
                                       max_iterations: int) -> List[Tuple]:
        """Generate realistic quantity combinations respecting min/max constraints."""
        quantities = []
        
        # Get min/max for each food
        constraints = []
        for food_key in food_combo:
            macros = self.calc.get_food_macros(food_key, 100)
            min_qty = macros.get("min_serving_g", 50)
            max_qty = macros.get("max_serving_g", 500)
            constraints.append((min_qty, max_qty))
        
        # Generate combinations within constraints
        for i in range(max_iterations):
            combo = []
            for min_qty, max_qty in constraints:
                # Vary between min and max
                step = (max_qty - min_qty) // max_iterations
                qty = min_qty + (i * step)
                combo.append(max(min_qty, min(qty, max_qty)))
            quantities.append(tuple(combo))
        
        return quantities
    
    def _apply_serving_granularity(self, plan: List[Dict]) -> List[Dict]:
        """
        Round quantities to serving sizes for human readability.
        
        Example: 410g eggs → 7 eggs (60g each)
        """
        adjusted_plan = []
        for item in plan:
            food_key = item["food"]
            qty_g = item["quantity_g"]
            
            # Round to serving
            rounded_qty, num_servings = self.calc.round_to_serving(food_key, qty_g)
            
            # Recalculate macros with rounded quantity
            macros = self.calc.get_food_macros(food_key, rounded_qty)
            
            adjusted_plan.append({
                "food": food_key,
                "quantity_g": rounded_qty,
                "num_servings": num_servings,
                "calories": macros["calories"],
                "protein_g": macros["protein_g"],
                "fat_g": macros["fat_g"],
                "carb_g": macros["carb_g"],
                "fiber_g": macros["fiber_g"],
                "iron_mg": macros.get("iron_mg", 0),
                "calcium_mg": macros.get("calcium_mg", 0),
                "vitamin_d_mcg": macros.get("vitamin_d_mcg", 0),
                "vitamin_c_mg": macros.get("vitamin_c_mg", 0),
                "potassium_mg": macros.get("potassium_mg", 0),
                "category": item.get("category", "mixed"),
            })
        
        return adjusted_plan
    
    def calculate_plan_totals(self, plan: List[Dict]) -> Dict:
        """Calculate total macros and micronutrients for a plan."""
        totals = {
            "total_calories": 0,
            "total_protein_g": 0,
            "total_fat_g": 0,
            "total_carb_g": 0,
            "total_fiber_g": 0,
            "total_iron_mg": 0,
            "total_calcium_mg": 0,
            "total_vitamin_d_mcg": 0,
            "total_vitamin_c_mg": 0,
            "total_potassium_mg": 0,
        }
        
        for item in plan:
            totals["total_calories"] += item["calories"]
            totals["total_protein_g"] += item["protein_g"]
            totals["total_fat_g"] += item["fat_g"]
            totals["total_carb_g"] += item["carb_g"]
            totals["total_fiber_g"] += item["fiber_g"]
            totals["total_iron_mg"] += item.get("iron_mg", 0)
            totals["total_calcium_mg"] += item.get("calcium_mg", 0)
            totals["total_vitamin_d_mcg"] += item.get("vitamin_d_mcg", 0)
            totals["total_vitamin_c_mg"] += item.get("vitamin_c_mg", 0)
            totals["total_potassium_mg"] += item.get("potassium_mg", 0)
        
        return {k: round(v, 1) for k, v in totals.items()}
    
    def distribute_to_meals(self, plan: List[Dict]) -> Dict:
        """
        Intelligently distribute plan across meals (breakfast/lunch/dinner).
        Uses food categories and meal compatibility to create realistic meals.
        
        Returns dict: {
            "breakfast": [items],
            "lunch": [items],
            "dinner": [items],
        }
        """
        meals = {
            "breakfast": {"foods": [], "calories": 0, "protein_g": 0, "micronutrients": {}},
            "lunch": {"foods": [], "calories": 0, "protein_g": 0, "micronutrients": {}},
            "dinner": {"foods": [], "calories": 0, "protein_g": 0, "micronutrients": {}},
        }
        
        totals = self.calculate_plan_totals(plan)
        total_cals = totals["total_calories"]
        
        # Define meal preferences
        breakfast_types = ["egg", "bread", "milk"]  # Breakfast staples
        lunch_types = ["rice", "bread", "chicken", "fish", "lentil", "chickpea"]  # Lunch items
        dinner_types = ["rice", "bread", "beef", "chicken", "fish", "lentil", "chickpea"]  # Dinner items
        
        # Target distribution
        breakfast_target = total_cals * 0.25  # 25% of daily
        lunch_target = total_cals * 0.40      # 40% of daily
        dinner_target = total_cals * 0.35     # 35% of daily
        
        # Sort by category compatibility
        remaining = list(plan)
        
        # Helper to add item to meal
        def add_to_meal(item, meal_name):
            meals[meal_name]["foods"].append(item)
            meals[meal_name]["calories"] += item["calories"]
            meals[meal_name]["protein_g"] += item["protein_g"]
            for micronut in ["iron_mg", "calcium_mg", "vitamin_d_mcg", "vitamin_c_mg", "potassium_mg"]:
                if micronut not in meals[meal_name]["micronutrients"]:
                    meals[meal_name]["micronutrients"][micronut] = 0
                meals[meal_name]["micronutrients"][micronut] += item.get(micronut, 0)
        
        # Phase 1: Assign preferred items to meals
        for meal_name, preference_list, target in [
            ("breakfast", breakfast_types, breakfast_target),
            ("lunch", lunch_types, lunch_target),
            ("dinner", dinner_types, dinner_target),
        ]:
            for food_type in preference_list:
                for item in list(remaining):
                    if item["food"] == food_type:
                        add_to_meal(item, meal_name)
                        remaining.remove(item)
                        if meals[meal_name]["calories"] >= target * 0.9:
                            break
                if meals[meal_name]["calories"] >= target * 0.9:
                    break
        
        # Phase 2: Distribute remaining items to balance meals
        for item in remaining:
            # Add to meal with lowest calories
            meal_cals = {
                "breakfast": meals["breakfast"]["calories"],
                "lunch": meals["lunch"]["calories"],
                "dinner": meals["dinner"]["calories"],
            }
            smallest_meal = min(meal_cals, key=meal_cals.get)
            add_to_meal(item, smallest_meal)
        
        return meals
