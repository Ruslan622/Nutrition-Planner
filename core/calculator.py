"""
NutritionCalculator
Calculates TDEE, macro targets based on user profile and goal.
No scraping. No printing. Pure calculations only.
"""

import json
from pathlib import Path


class NutritionCalculator:
    """Calculate nutrition targets for bulk, cut, maintain goals."""
    
    def __init__(self, config_file: str = None):
        """
        Initialize calculator with config.
        
        Args:
            config_file: Path to config.py (will import ACTIVITY_LEVELS and GOALS)
        """
        # Import from config
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from config import ACTIVITY_LEVELS, GOALS
        
        self.ACTIVITY_LEVELS = ACTIVITY_LEVELS
        self.GOALS = GOALS
        
        # Load food data
        self.food_data = self._load_food_data()
    
    def _load_food_data(self) -> dict:
        """Load food macros from JSON."""
        food_file = Path(__file__).parent.parent / "data" / "food_macros.json"
        with open(food_file, 'r') as f:
            raw_data = json.load(f)
        
        # Filter out metadata fields (those starting with _)
        data = {k: v for k, v in raw_data.items() if not k.startswith('_')}
        return data
    
    def calculate_tdee(self, 
                       age: int, 
                       weight_kg: float, 
                       height_cm: float, 
                       sex: str,  # "M" or "F"
                       activity_level: int) -> float:
        """
        Calculate Total Daily Energy Expenditure (TDEE).
        
        Uses Mifflin-St Jeor for BMR, then applies activity multiplier (PAL).
        
        Args:
            age: Age in years
            weight_kg: Weight in kg
            height_cm: Height in cm
            sex: "M" for male, "F" for female
            activity_level: 1-5 (sedentary to extra active)
            
        Returns:
            TDEE in kcal
        """
        # Mifflin-St Jeor BMR formula
        if sex.upper() == "M":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:  # F
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
        # Apply activity multiplier
        activity_factor = self.ACTIVITY_LEVELS[str(activity_level)]["factor"]
        tdee = bmr * activity_factor
        
        return round(tdee, 0)
    
    def calculate_targets(self,
                         tdee: float,
                         weight_kg: float,
                         goal: str) -> dict:
        """
        Calculate macro targets (calories, protein, fat) based on goal.
        
        Args:
            tdee: Total Daily Energy Expenditure
            weight_kg: Weight in kg
            goal: "maintenance", "loss", or "gain"
            
        Returns:
            Dict with target_calories, target_protein_g, target_fat_g, target_carb_g
        """
        # Find goal config
        goal_config = None
        for goal_key, config in self.GOALS.items():
            if config["key"] == goal:
                goal_config = config
                break
        
        if not goal_config:
            raise ValueError(f"Unknown goal: {goal}")
        
        # Calculate targets
        target_calories = tdee + goal_config["calorie_delta"]
        target_protein_g = weight_kg * goal_config["protein_per_kg"]
        target_fat_g = (target_calories * goal_config["fat_pct"]) / 9  # 9 kcal/g
        target_carb_g = (target_calories - (target_protein_g * 4) - (target_fat_g * 9)) / 4  # 4 kcal/g
        
        return {
            "target_calories": round(target_calories, 0),
            "target_protein_g": round(target_protein_g, 1),
            "target_fat_g": round(target_fat_g, 1),
            "target_carb_g": round(target_carb_g, 1),
        }
    
    def get_food_macros(self, food_key: str, quantity_g: float = 100) -> dict:
        """
        Get macro values for a food at given quantity.
        
        Args:
            food_key: Key in food_macros.json (e.g., "rice", "chicken")
            quantity_g: Quantity in grams
            
        Returns:
            Dict with calories, protein_g, fat_g, carb_g, fiber_g, category, constraints
        """
        if food_key not in self.food_data:
            raise ValueError(f"Food '{food_key}' not in database")
        
        food = self.food_data[food_key]
        multiplier = quantity_g / 100
        
        return {
            "food": food_key,
            "quantity_g": quantity_g,
            "calories": round(food["cal_per_100"] * multiplier, 1),
            "protein_g": round(food["pro_per_100"] * multiplier, 1),
            "fat_g": round(food["fat_per_100"] * multiplier, 1),
            "carb_g": round(food["carb_per_100"] * multiplier, 1),
            "fiber_g": round(food["fiber_per_100"] * multiplier, 1),
            "category": food.get("category", "other"),
            "min_serving_g": food.get("min_serving_g", 50),
            "max_serving_g": food.get("max_serving_g", 500),
        }
    
    def get_food_name(self, food_key: str) -> str:
        """Get display name for a food."""
        if food_key in self.food_data:
            return self.food_data[food_key]["name"]
        return food_key
    
    def get_serving_info(self, food_key: str) -> dict:
        """Get serving unit and size for a food."""
        if food_key not in self.food_data:
            return {"serving_unit": "gram", "serving_size": 100}
        
        food = self.food_data[food_key]
        return {
            "serving_unit": food.get("serving_unit", "gram"),
            "serving_size": food.get("serving_size", 100),
        }
    
    def round_to_serving(self, food_key: str, quantity_g: float) -> tuple:
        """
        Round quantity to nearest serving.
        
        Returns: (rounded_quantity_g, num_servings)
        """
        serving_info = self.get_serving_info(food_key)
        serving_size = serving_info["serving_size"]
        
        num_servings = round(quantity_g / serving_size)
        num_servings = max(1, num_servings)  # At least 1 serving
        rounded_g = num_servings * serving_size
        
        return rounded_g, num_servings
    
    def get_food_category(self, food_key: str) -> str:
        """Get category of a food."""
        if food_key in self.food_data:
            return self.food_data[food_key].get("category", "mixed")
        return "mixed"
    
    def get_food_meal_types(self, food_key: str) -> list:
        """Get suitable meal types for a food."""
        if food_key in self.food_data:
            return self.food_data[food_key].get("meal_types", ["lunch", "dinner"])
        return ["lunch", "dinner"]
    
    def get_compatible_foods(self, food_key: str) -> list:
        """Get foods compatible with this food."""
        if food_key in self.food_data:
            return self.food_data[food_key].get("compatible_with", [])
        return []
    
    def get_serving_constraints(self, food_key: str) -> dict:
        """Get min/max serving constraints for a food."""
        if food_key not in self.food_data:
            return {"min_serving_g": 50, "max_serving_g": 500}
        
        food = self.food_data[food_key]
        return {
            "min_serving_g": food.get("min_serving_g", 50),
            "max_serving_g": food.get("max_serving_g", 500),
        }
    
    def available_foods(self) -> list:
        """Return list of available food keys."""
        return list(self.food_data.keys())
