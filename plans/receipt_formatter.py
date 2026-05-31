"""
Receipt Formatter v2
Generates clean, human-readable meal plan receipts for non-technical users.
Supports both text and PDF output (PDF is primary).
"""

from typing import List, Dict
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


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
            
            lines.append(f"│ {food_name:<27} {qty_display:>8} Tk. {cost:>7.2f} {protein:>9.1f}g {calories:>9.0f} kcal      │")
        
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        
        # Totals line
        total_cost = cost_info["total_cost_bdt"]
        total_protein = totals["total_protein_g"]
        total_calories = totals["total_calories"]
        lines.append(f"│ TOTAL (Daily):               {'':>8} Tk. {total_cost:>7.2f} {total_protein:>9.1f}g {total_calories:>9.0f} kcal      │")
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
            lines.append(f"│ {food_name:<20} Tk. {cost:>7.2f}/day      Tk. {monthly:>7.2f}/month  {pct:>5.1f}% {bar:<15}│")
        
        lines.append("├─────────────────────────────────────────────────────────────────────────────┤")
        monthly_total = total_cost * 30
        lines.append(f"│ TOTAL:               Tk. {total_cost:>7.2f}/day      Tk. {monthly_total:>7.2f}/month  100.0%                    │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        # Cost efficiency metrics
        lines.append("\n┌─ COST EFFICIENCY METRICS ──────────────────────────────────────────────────────┐")
        lines.append(f"│ Cost per 1000 kcal:        Tk. {cost_info['total_cost_bdt'] / (total_calories/1000):>6.2f}                                          │")
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
                lines.append(f"│ {mode_label} Tk. {daily:>7.2f}        Tk. {monthly:>7.2f}        {protein:>6.1f}g         {quality:>4.1f}/10        │")
        
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        # Recommendations
        lines.append("\n┌─ RECOMMENDATIONS ──────────────────────────────────────────────────────────────┐")
        if "cheapest" in plans_by_mode and "premium" in plans_by_mode:
            cheapest = plans_by_mode["cheapest"][1]["daily_cost_bdt"]
            premium = plans_by_mode["premium"][1]["daily_cost_bdt"]
            diff = premium - cheapest
            lines.append(f"│ Premium costs Tk. {diff:.2f} more per day than Cheapest plan.                          │")
            lines.append(f"│ That's about Tk. {diff*30:.2f} per month for higher quality nutrition.                    │")
        
        lines.append("│                                                                             │")
        lines.append("│ 🎯 Choose CHEAPEST if your budget is very tight.                             │")
        lines.append("│ ⚖️  Choose BALANCED for good value - recommended for most people.            │")
        lines.append("│ ⭐ Choose PREMIUM if fitness/performance is your priority.                   │")
        lines.append("└─────────────────────────────────────────────────────────────────────────────┘")
        
        return "\n".join(lines)
    
    def save_meal_receipt_pdf(self,
                             filepath: str,
                             plan: List[Dict],
                             totals: Dict,
                             cost_info: Dict,
                             metrics: Dict = None,
                             user_profile: Dict = None) -> bool:
        """
        Save meal plan as PDF receipt.
        
        Args:
            filepath: Path to save PDF to
            plan: Meal plan
            totals: Nutritional totals
            cost_info: Cost breakdown
            metrics: Optimization metrics (optional)
            user_profile: User info (optional)
            
        Returns:
            True if successful
        """
        try:
            # Create PDF
            doc = SimpleDocTemplate(filepath, pagesize=letter,
                                   rightMargin=0.5*inch, leftMargin=0.5*inch,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            
            story = []
            
            # Header
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=getSampleStyleSheet()['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#2E7D32'),
                spaceAfter=6,
                alignment=TA_CENTER
            )
            story.append(Paragraph("🥗 NUTRIBUDGET BD MEAL PLAN 🥗", title_style))
            
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=getSampleStyleSheet()['Normal'],
                fontSize=12,
                alignment=TA_CENTER,
                spaceAfter=12
            )
            story.append(Paragraph("Daily Nutrition Receipt", subtitle_style))
            
            # Date and user info
            today = datetime.now().strftime("%d %B %Y")
            info_text = f"<b>Date:</b> {today}"
            if user_profile:
                info_text += f" | <b>User:</b> {user_profile.get('weight_kg', '?')}kg"
                info_text += f" | <b>Goal:</b> {user_profile.get('goal', 'maintenance').title()}"
            if metrics and "budget_mode" in metrics:
                info_text += f" | <b>Plan:</b> {metrics['budget_mode'].upper()}"
            
            story.append(Paragraph(info_text, getSampleStyleSheet()['Normal']))
            story.append(Spacer(1, 0.2*inch))
            
            # Nutrition targets table
            story.append(Paragraph("<b>Daily Nutrition Targets</b>", getSampleStyleSheet()['Heading3']))
            targets_data = [
                [f"Calories: {totals['total_calories']:.0f} kcal", 
                 f"Protein: {totals['total_protein_g']:.1f}g"],
                [f"Fat: {totals['total_fat_g']:.1f}g",
                 f"Carbs: {totals['total_carb_g']:.1f}g"],
            ]
            targets_table = Table(targets_data, colWidths=[3.5*inch, 3.5*inch])
            targets_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8F5E9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('PADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(targets_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Foods table
            story.append(Paragraph("<b>Daily Foods (Itemized)</b>", getSampleStyleSheet()['Heading3']))
            foods_data = [["Food Item", "Quantity", "Cost", "Protein", "Calories"]]
            
            for item in sorted(plan, key=lambda x: cost_info["cost_breakdown"].get(x["food"], 0), reverse=True):
                food_key = item["food"]
                food_name = self.calc.get_food_name(food_key)
                cost = cost_info["cost_breakdown"].get(food_key, 0)
                protein = item["protein_g"]
                calories = item["calories"]
                
                # Format qty
                serving_info = self.calc.get_serving_info(food_key)
                serving_unit = serving_info["serving_unit"]
                if serving_unit == "piece":
                    qty_display = f"{item.get('num_servings', 1):.0f} pcs"
                elif serving_unit in ["cup", "slice"]:
                    qty_display = f"{item.get('num_servings', 1):.0f} {serving_unit}s"
                else:
                    qty_display = f"{item['quantity_g']:.0f}g"
                
                foods_data.append([
                    food_name[:25],
                    qty_display,
                    f"Tk. {cost:.2f}",
                    f"{protein:.1f}g",
                    f"{calories:.0f} kcal"
                ])
            
            # Add total row
            total_cost = cost_info["total_cost_bdt"]
            total_protein = totals["total_protein_g"]
            total_calories = totals["total_calories"]
            foods_data.append([
                "<b>TOTAL (Daily)</b>",
                "",
                f"<b>Tk. {total_cost:.2f}</b>",
                f"<b>{total_protein:.1f}g</b>",
                f"<b>{total_calories:.0f} kcal</b>"
            ])
            
            foods_table = Table(foods_data, colWidths=[2.2*inch, 1.2*inch, 1*inch, 1*inch, 1.1*inch])
            foods_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F1F8E9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
            ]))
            story.append(foods_table)
            story.append(Spacer(1, 0.15*inch))
            
            # Cost breakdown table
            story.append(Paragraph("<b>Budget Breakdown</b>", getSampleStyleSheet()['Heading3']))
            cost_data = [["Food Item", "Daily Cost", "Monthly Cost", "% of Budget"]]
            
            for food_key, cost in sorted(cost_info["cost_breakdown"].items(), key=lambda x: x[1], reverse=True):
                food_name = self.calc.get_food_name(food_key)
                monthly = cost * 30
                pct = (cost / total_cost) * 100 if total_cost > 0 else 0
                cost_data.append([
                    food_name[:20],
                    f"Tk. {cost:.2f}/day",
                    f"Tk. {monthly:.2f}/month",
                    f"{pct:.1f}%"
                ])
            
            cost_data.append([
                "<b>TOTAL</b>",
                f"<b>Tk. {total_cost:.2f}/day</b>",
                f"<b>Tk. {total_cost*30:.2f}/month</b>",
                "<b>100.0%</b>"
            ])
            
            cost_table = Table(cost_data, colWidths=[2*inch, 1.5*inch, 1.8*inch, 1.2*inch])
            cost_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9800')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFF3E0')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
            ]))
            story.append(cost_table)
            story.append(Spacer(1, 0.15*inch))
            
            # Efficiency metrics
            story.append(Paragraph("<b>Cost Efficiency Metrics</b>", getSampleStyleSheet()['Heading3']))
            metrics_data = [
                [f"Cost per 1000 kcal:", f"Tk. {total_cost / (total_calories/1000):.2f}"],
                [f"Protein per Taka:", f"{(total_protein/total_cost):.3f}g"],
            ]
            metrics_table = Table(metrics_data, colWidths=[3*inch, 3*inch])
            metrics_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E3F2FD')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]))
            story.append(metrics_table)
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"ERROR creating PDF: {e}")
            return False
    
    def save_budget_comparison_pdf(self,
                                  filepath: str,
                                  plans_by_mode: Dict) -> bool:
        """
        Save budget comparison as PDF.
        
        Args:
            filepath: Path to save PDF to
            plans_by_mode: Dict mapping mode → (plan, metrics)
            
        Returns:
            True if successful
        """
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter,
                                   rightMargin=0.5*inch, leftMargin=0.5*inch,
                                   topMargin=0.5*inch, bottomMargin=0.5*inch)
            
            story = []
            
            # Header
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=getSampleStyleSheet()['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#FF6F00'),
                spaceAfter=12,
                alignment=TA_CENTER
            )
            story.append(Paragraph("💰 BUDGET MODE COMPARISON 💰", title_style))
            
            # Comparison table
            story.append(Paragraph("<b>Cost Comparison</b>", getSampleStyleSheet()['Heading3']))
            
            comp_data = [["Plan Type", "Daily Cost", "Monthly Cost", "Protein/Day", "Quality Score"]]
            for mode in ["cheapest", "balanced", "premium"]:
                if mode in plans_by_mode:
                    plan, metrics = plans_by_mode[mode]
                    daily = metrics["daily_cost_bdt"]
                    monthly = metrics["monthly_cost_bdt"]
                    protein = metrics["total_protein_g"]
                    quality = metrics.get("avg_protein_quality", 5.0)
                    
                    comp_data.append([
                        mode.upper(),
                        f"Tk. {daily:.2f}",
                        f"Tk. {monthly:.2f}",
                        f"{protein:.1f}g",
                        f"{quality:.1f}/10"
                    ])
            
            comp_table = Table(comp_data, colWidths=[1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
            comp_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976D2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ]))
            story.append(comp_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Recommendations
            story.append(Paragraph("<b>Recommendations</b>", getSampleStyleSheet()['Heading3']))
            
            if "cheapest" in plans_by_mode and "premium" in plans_by_mode:
                cheapest = plans_by_mode["cheapest"][1]["daily_cost_bdt"]
                premium = plans_by_mode["premium"][1]["daily_cost_bdt"]
                diff = premium - cheapest
                monthly_diff = diff * 30
                
                rec_text = f"""
                <b>Cost Difference:</b> Premium costs Tk. {diff:.2f} more per day than Cheapest plan.<br/>
                That's about Tk. {monthly_diff:.2f} per month for higher quality nutrition.<br/>
                <br/>
                <b>🎯 Choose CHEAPEST</b> if your budget is very tight.<br/>
                <b>⚖️ Choose BALANCED</b> for good value - recommended for most people.<br/>
                <b>⭐ Choose PREMIUM</b> if fitness/performance is your priority.
                """
                story.append(Paragraph(rec_text, getSampleStyleSheet()['Normal']))
            
            # Build PDF
            doc.build(story)
            return True
            
        except Exception as e:
            print(f"ERROR creating comparison PDF: {e}")
            return False
