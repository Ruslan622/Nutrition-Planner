"""
Price Manager v1
Loads, cleans, normalizes, and manages food prices.
Core responsibility: standardize all prices to price_per_100g for comparison.
"""

import json
from pathlib import Path
from typing import Dict, Tuple


class PriceManager:
    """
    Load and normalize food prices to common unit (price_per_100g).
    
    Handles conversions:
    - kg → price_per_100g
    - piece → price_per_100g (requires grams_each from food macros)
    - litre → price_per_100g (assume 1 litre ≈ 1000g for liquids)
    """
    
    # Unit conversion factors (to grams)
    UNIT_TO_GRAMS = {
        "kg": 1000,
        "piece": None,  # Requires grams_each from food data
        "litre": 1000,  # Assume 1 litre = 1000g (density ≈ 1)
        "ml": 1,  # 1 ml ≈ 1g for liquids
        "gram": 1,
        "g": 1,
    }
    
    def __init__(self, price_file: str = None, food_data: dict = None):
        """
        Initialize price manager.
        
        Args:
            price_file: Path to food_prices.json (optional, auto-detected if None)
            food_data: Dictionary of food macros (needed for piece → grams conversion)
        """
        if price_file is None:
            price_file = Path(__file__).parent.parent / "data" / "food_prices.json"
        
        self.price_file = price_file
        self.food_data = food_data or {}
        self.raw_prices = self._load_prices()
        self.normalized_prices = self._normalize_all_prices()
    
    def _load_prices(self) -> Dict:
        """Load raw prices from JSON file."""
        try:
            with open(self.price_file, 'r') as f:
                data = json.load(f)
            # Filter out metadata (keys starting with _)
            return {k: v for k, v in data.items() if not k.startswith('_')}
        except FileNotFoundError:
            print(f"ERROR: Price file not found: {self.price_file}")
            return {}
    
    def _normalize_all_prices(self) -> Dict[str, float]:
        """
        Normalize all prices to price_per_100g.
        
        Returns:
            Dict mapping food_key → price_per_100g (in BDT)
        """
        normalized = {}
        
        for food_key, price_info in self.raw_prices.items():
            normalized[food_key] = self._normalize_price(food_key, price_info)
        
        return normalized
    
    def _normalize_price(self, food_key: str, price_info: Dict) -> float:
        """
        Convert price to price_per_100g.
        
        Args:
            food_key: Food identifier
            price_info: Dict with 'price' and 'unit' keys
            
        Returns:
            Price per 100g in BDT
        """
        price = price_info.get("price", 0)
        unit = price_info.get("unit", "kg")
        
        if price <= 0:
            return 0
        
        # ─── Unit conversion ───────────────────────────────────────
        
        if unit in ["kg", "kilogram"]:
            # price is per kg → convert to per 100g
            price_per_100g = price / 10
            return round(price_per_100g, 2)
        
        elif unit in ["g", "gram"]:
            # price is per gram → convert to per 100g
            price_per_100g = price * 100
            return round(price_per_100g, 2)
        
        elif unit in ["piece", "pcs"]:
            # price is per piece → need grams_each from food_data
            if food_key not in self.food_data:
                print(f"WARNING: No food data for {food_key}, cannot convert piece price")
                return 0
            
            grams_each = self.food_data[food_key].get("grams_each", 100)
            price_per_100g = (price / grams_each) * 100
            return round(price_per_100g, 2)
        
        elif unit in ["litre", "liter", "l"]:
            # price is per litre → assume 1 litre ≈ 1000g
            price_per_100g = price / 10
            return round(price_per_100g, 2)
        
        elif unit in ["ml", "millilitre"]:
            # price is per ml → assume 1 ml ≈ 1g
            price_per_100g = (price / 1) * 100
            return round(price_per_100g, 2)
        
        else:
            print(f"WARNING: Unknown unit '{unit}' for {food_key}")
            return 0
    
    def get_price_per_100g(self, food_key: str) -> float:
        """
        Get normalized price per 100g for a food.
        
        Args:
            food_key: Food identifier (e.g., "rice", "chicken")
            
        Returns:
            Price per 100g in BDT
        """
        return self.normalized_prices.get(food_key, 0)
    
    def get_price_for_quantity(self, food_key: str, quantity_g: float) -> float:
        """
        Calculate cost for a given quantity of food.
        
        Args:
            food_key: Food identifier
            quantity_g: Quantity in grams
            
        Returns:
            Total cost in BDT
        """
        price_per_100g = self.get_price_per_100g(food_key)
        return round((quantity_g / 100) * price_per_100g, 2)
    
    def get_raw_price(self, food_key: str) -> Tuple[float, str]:
        """
        Get raw price and unit (for reference/debugging).
        
        Args:
            food_key: Food identifier
            
        Returns:
            Tuple (price, unit)
        """
        if food_key in self.raw_prices:
            info = self.raw_prices[food_key]
            return info.get("price"), info.get("unit")
        return 0, "unknown"
    
    def get_all_normalized_prices(self) -> Dict[str, float]:
        """Get all foods with their price_per_100g."""
        return self.normalized_prices.copy()
    
    def rank_by_price(self, foods: list = None, ascending: bool = True) -> list:
        """
        Rank foods by price_per_100g.
        
        Args:
            foods: List of food keys to rank (None = all foods)
            ascending: If True, cheapest first; False = most expensive first
            
        Returns:
            List of (food_key, price_per_100g) tuples, sorted
        """
        if foods is None:
            foods = list(self.normalized_prices.keys())
        
        rankings = [
            (food, self.normalized_prices.get(food, 0))
            for food in foods
            if food in self.normalized_prices
        ]
        
        rankings.sort(key=lambda x: x[1], reverse=not ascending)
        return rankings
    
    def print_price_summary(self, foods: list = None):
        """Print a summary of all prices (for debugging)."""
        print("\n" + "="*70)
        print("PRICE SUMMARY (Normalized to BDT per 100g)")
        print("="*70)
        
        rankings = self.rank_by_price(foods, ascending=True)
        
        print(f"{'Food':<15} {'Price/100g (BDT)':<18} {'Raw Price':<15}")
        print("-"*70)
        
        for food_key, price_per_100g in rankings:
            raw_price, raw_unit = self.get_raw_price(food_key)
            print(f"{food_key:<15} {price_per_100g:<18.2f} {raw_price} {raw_unit}")
        
        print("="*70 + "\n")
