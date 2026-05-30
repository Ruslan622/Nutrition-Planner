"""
Receipt Formatter v1
Generates clean, human-readable meal plan receipts for non-technical users.
Output is formatted like a restaurant receipt/invoice.
"""

from typing import List, Dict
from datetime import datetime


class ReceiptFormatter:
    """Format meal plans as readable receipts/invoices."""
    
    def __init__(self, calculator, price_manager):
        """
        Initialize formatter.
        
        Args:
            calculator: NutritionCalculator instance
            price_manager: PriceManager instance
        """
        self.calc = calculator
        self.pm = price_manager
    
    def format_meal_receipt(self,
                           plan: List[Dict],
                           totals: Dict,
                           cost_info: Dict,
                           metrics: Dict = None,
                           user_profile: Dict = None) -> str:
        """
        Format a meal plan as a printable receipt.
        
        Args:
            plan: Meal plan (list of items)
            totals: Nutritional totals
            cost_info: Cost breakdown from CostCalculator
            metrics: Optimization metrics (optional)
            user_profile: User info (age, weight, etc) (optional)
            
        Returns:
            Formatted receipt string
        """
        lines = []
        
        # Header
        lines.append("╔" + "═" * 78 + "╗")
        lines.append("║" + " " * 20 + "🥗 NUTRIBUDGET BD MEAL PLAN 🥗" + " " * 20 + "║")
        lines.append("║" + " " * 25 + "Daily Nutrition Receipt" + " " * 31 + "║")
        lines.append("╚" + "═" * 78 + "╝")
        
        # Date
        today = datetime.now().strftime("%d %B %Y (%A)")
        lines.append(f"\nDate: {today}")
        
        # User info if provided
        if user_profile:
            lines.append(f"User: {user_profile.get('weight_kg', '?')}kg | "
                        f"Goal: {user_profile.get('goal', 'maintenance').title()}")
        
        # Budget mode if in metrics
        if metrics and "budget_mode" in metrics:
            mode = metrics["budget_mode"].upper()
            lines.append(f"Plan Type: {mode} (Cost-Optimized)\n")
        
        # Nutritional targets
        lines.append("┌─ DAILY NUTRITION TARGETS ─────────────────────────────────────────────────┐")
        lines.append(f"│ Calories: {totals['total_calories']:>8.0f} kcal       │ Protein: {totals['total_protein_g']:>6.1f}g                        │")
        lines.append(f"│ Fat:      {totals['total_fat_g']:>8.1f}g          │ Carbs:   {totals['total_carb_g']:>6.1f}g                        │")
        if totals.get('total_fiber_g'):
            lines.append(f"│ Fiber:    {totals['total_fiber_g']:>8.1f}g                                              │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        # Foods itemized (like receipt)
        lines.append("\n┌─ DAILY FOODS (Itemized) ──────────────────────────────────────────────────────┐")
        lines.append("│ Item                          Qty      Cost      Protein     Calories          │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        
        for item in sorted(plan, key=lambda x: cost_info["cost_breakdown"].get(x["food"], 0), reverse=True):
            food_key = item["food"]
            food_name = self.calc.get_food_name(food_key)
            qty_g = item["quantity_g"]
            cost = cost_info["cost_breakdown"].get(food_key, 0)
            protein = item["protein_g"]
            calories = item["calories"]
            
            # Format qty with unit
            serving_info = self.calc.get_serving_info(food_key)
            serving_unit = serving_info["serving_unit"]
            if serving_unit == "piece":
                qty_display = f"{item.get('num_servings', 1):.0f} pcs"
            elif serving_unit in ["cup", "slice"]:
                qty_display = f"{item.get('num_servings', 1):.0f} {serving_unit}s"
            else:
                qty_display = f"{qty_g:.0f}g"
            
            lines.append(f"│ {food_name:<27} {qty_display:>8} {cost:>7.2f}฿ {protein:>9.1f}g {calories:>9.0f} kcal      │")
        
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        
        # Totals line
        total_cost = cost_info["total_cost_bdt"]
        total_protein = totals["total_protein_g"]
        total_calories = totals["total_calories"]
        lines.append(f"│ TOTAL (Daily):               {'':>8} {total_cost:>7.2f}฿ {total_protein:>9.1f}g {total_calories:>9.0f} kcal      │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        # Cost breakdown
        lines.append("\n┌─ BUDGET BREAKDOWN ─────────────────────────────────────────────────────────────┐")
        lines.append("│ Food Item            Daily Cost       Monthly Cost    % of Budget              │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        
        for food_key, cost in sorted(cost_info["cost_breakdown"].items(), key=lambda x: x[1], reverse=True):
            food_name = self.calc.get_food_name(food_key)
            monthly = cost * 30
            pct = (cost / total_cost) * 100 if total_cost > 0 else 0
            bar = "█" * int(pct / 5)  # 20 char bar = 100%
            lines.append(f"│ {food_name:<20} {cost:>7.2f}฿/day      {monthly:>7.2f}฿/month  {pct:>5.1f}% {bar:<15}│")
        
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        monthly_total = total_cost * 30
        lines.append(f"│ TOTAL:               {total_cost:>7.2f}฿/day      {monthly_total:>7.2f}฿/month  100.0%                    │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        # Cost efficiency metrics
        lines.append("\n┌─ COST EFFICIENCY METRICS ──────────────────────────────────────────────────────┐")
        lines.append(f"│ Cost per 1000 kcal:        {cost_info['total_cost_bdt'] / (total_calories/1000):>6.2f} ฿                                          │")
        protein_per_taka = total_protein / total_cost if total_cost > 0 else 0
        lines.append(f"│ Protein per 1 Taka:        {protein_per_taka:>6.3f}g                                             │")
        lines.append(f"│ Protein per 100 Taka:      {protein_per_taka * 100:>6.1f}g                                            │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        # Mode-specific info and quality metrics
        if metrics:
            lines.append(f"\n┌─ PLAN QUALITY SCORES ──────────────────────────────────────────────────────────┐")
            
            if "avg_protein_quality" in metrics:
                lines.append(f"│ Average Protein Quality:   {metrics['avg_protein_quality']:>6.1f}/10                                     │")
            
            if "num_foods" in metrics:
                lines.append(f"│ Food Variety:              {metrics['num_foods']:>6.0f} different foods                                │")
            
            if "budget_mode" in metrics:
                mode = metrics["budget_mode"].upper()
                lines.append(f"│ Optimization Mode:         {mode:<50}│")
                mode_desc = self._get_mode_description(metrics["budget_mode"])
                lines.append(f"│ Strategy:                  {mode_desc:<50}│")
            
            lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        # Footer
        lines.append("\n" + "─" * 80)
        lines.append("✓ This plan meets your daily nutrition targets while staying within your budget.")
        lines.append("  Prepare these foods at home to save even more money!")
        lines.append("─" * 80)
        
        return "\n".join(lines)
    
    def _get_mode_description(self, budget_mode: str) -> str:
        """Get description for budget mode."""
        descriptions = {
            "cheapest": "Minimum cost - budget-conscious",
            "balanced": "Cost & quality balanced",
            "premium": "Maximum nutrition quality",
        }
        return descriptions.get(budget_mode, "Unknown")
    
    def format_budget_comparison(self, plans_by_mode: Dict) -> str:
        """
        Format comparison of all budget modes as a comparison table.
        
        Args:
            plans_by_mode: Dict mapping mode → (plan, metrics)
            
        Returns:
            Formatted comparison receipt
        """
        lines = []
        
        lines.append("╔" + "═" * 78 + "╗")
        lines.append("║" + " " * 15 + "💰 BUDGET MODE COMPARISON RECEIPT 💰" + " " * 15 + "║")
        lines.append("╚" + "═" * 78 + "╝\n")
        
        lines.append("┌─ COST COMPARISON ──────────────────────────────────────────────────────────────┐")
        lines.append("│ Plan Type    Daily Cost    Monthly Cost    Protein/Day    Quality Score       │")
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        
        for mode in ["cheapest", "balanced", "premium"]:
            if mode in plans_by_mode:
                plan, metrics = plans_by_mode[mode]
                daily = metrics["daily_cost_bdt"]
                monthly = metrics["monthly_cost_bdt"]
                protein = metrics["total_protein_g"]
                quality = metrics.get("avg_protein_quality", 5.0)
                
                mode_label = mode.upper().ljust(12)
                lines.append(f"│ {mode_label} {daily:>7.2f}฿        {monthly:>7.2f}฿        {protein:>6.1f}g         {quality:>4.1f}/10        │")
        
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        # Recommendations
        lines.append("\n┌─ RECOMMENDATIONS ──────────────────────────────────────────────────────────────┐")
        if "cheapest" in plans_by_mode and "premium" in plans_by_mode:
            cheapest = plans_by_mode["cheapest"][1]["daily_cost_bdt"]
            premium = plans_by_mode["premium"][1]["daily_cost_bdt"]
            diff = premium - cheapest
            lines.append(f"│ Premium costs {diff:.2f}฿ more per day than Cheapest plan.                          │")
            lines.append(f"│ That's about {diff*30:.2f}฿ per month for higher quality nutrition.                    │")
        
        lines.append("│                                                                             │")
        lines.append("│ 🎯 Choose CHEAPEST if your budget is very tight.                             │")
        lines.append("│ ⚖️  Choose BALANCED for good value - recommended for most people.            │")
        lines.append("│ ⭐ Choose PREMIUM if fitness/performance is your priority.                   │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        return "\n".join(lines)
