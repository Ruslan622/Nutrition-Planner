"""
REST API for Nutrition Planner using FastAPI
Exposes meal plan generation endpoints
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from core.calculator import NutritionCalculator
from core.planner import MealPlanner
from core.cost_calculator import CostCalculator
from core.optimizer import Optimizer
from scraper.price_manager import PriceManager
from plans.receipt_formatter import ReceiptFormatter

app = FastAPI(title="Nutrition Planner API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
calc = NutritionCalculator()
planner = MealPlanner(calc)
pm = PriceManager(food_data=calc.food_data)
cc = CostCalculator(pm)
opt = Optimizer(calc, planner, pm, cc)
formatter = ReceiptFormatter(calc, pm)


class UserProfile(BaseModel):
    age: int
    weight_kg: float
    height_cm: float
    sex: str = "M"
    activity_level: int = 3
    goal: str


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/generate-plan")
def generate_plan(user: UserProfile):
    """
    Generate a meal plan based on user input.
    
    Request JSON:
    {
        "age": 28,
        "weight_kg": 75,
        "height_cm": 180,
        "sex": "M",
        "activity_level": 3,
        "goal": "maintenance"
    }
    
    Response:
    {
        "tdee": 2697,
        "targets": {...},
        "plans": {
            "cheapest": {...},
            "balanced": {...},
            "premium": {...}
        }
    }
    """
    try:
        # Calculate TDEE and targets
        tdee = calc.calculate_tdee(
            age=user.age,
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            sex=user.sex,
            activity_level=user.activity_level
        )
        
        targets = calc.calculate_targets(
            tdee=tdee,
            weight_kg=user.weight_kg,
            goal=user.goal
        )
        
        # Generate plans for all modes
        plans_by_mode = opt.generate_plans_all_modes(
            target_calories=targets["target_calories"],
            target_protein_g=targets["target_protein_g"],
            target_fat_g=targets["target_fat_g"],
            target_carb_g=targets["target_carb_g"],
            tolerance_calories=150,
            tolerance_protein=10,
        )
        
        if not plans_by_mode:
            raise HTTPException(status_code=400, detail="No plans generated")
        
        # Format response
        response = {
            "tdee": tdee,
            "targets": targets,
            "plans": {}
        }
        
        for mode, (plan, metrics) in plans_by_mode.items():
            totals = planner.calculate_plan_totals(plan)
            cost_info = cc.calculate_plan_cost(plan)
            meals = planner.distribute_to_meals(plan)
            
            # Format plan data for frontend
            response["plans"][mode] = {
                "foods": plan,
                "meals": meals,
                "totals": totals,
                "cost": cost_info,
                "metrics": metrics,
            }
        
        return response
        
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
