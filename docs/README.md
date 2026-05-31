# NutriBudget BD - Nutrition Planner

A personalized meal planning and nutrition optimization tool for Bangladesh-specific foods.

## 🚀 Quick Start

### Run Everything from One Place
```bash
python run.py
```

This opens an interactive menu where you can:
- **Run Interactive Planner** - Get personalized meal plans based on your profile
- **Run All Tests** - Verify everything works correctly
- **Debug Tools** - Run individual test files and debug scripts
- **View Reports** - Open generated meal plans and budgets

### Initial Setup
```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 3. Install dependencies (if needed)
pip install -r requirements.txt
```

## 📁 Project Structure

```
core/              - Core calculation & optimization logic
  ├── calculator.py    - Nutrition calculations
  ├── optimizer.py     - Meal plan optimization
  ├── planner.py       - Meal planning logic
  └── cost_calculator.py - Budget calculations

plans/             - Reporting & formatting
  ├── report.py        - Generate meal plan reports
  └── receipt_formatter.py

data/              - Food nutrition & price data
  ├── food_macros.json     - Nutritional info per 100g
  ├── food_prices.json     - Baseline prices
  └── prices_cache.json    - Cached prices from scrapers

output/            - Generated reports (gitignored)
  ├── meal_plan_*.txt
  ├── budget_*.txt
  └── *.pdf

run.py             - **MAIN ENTRY POINT** - Start here!
main.py            - Interactive mode (called from run.py)
```

## 🎯 What It Does

1. **Nutrition Planning** - Calculates TDEE, macro targets based on goals
2. **Meal Optimization** - Creates affordable meal plans within budget
3. **Budget Modes** - Cheapest, Balanced, or Premium options
4. **Reports** - Generates meal plans, shopping lists, budgets

## 📝 Output Files

All generated files are created in the `output/` folder and gitignored:
- Meal plan TXT files
- Budget comparisons
- Reports stay local (not uploaded to GitHub)

---

**Start with:** `python run.py`