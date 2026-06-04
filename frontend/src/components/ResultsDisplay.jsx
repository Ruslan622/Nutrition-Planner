import MacroRingsChart from "./MacroRingsChart";
import MealCard from "./MealCard";

export default function ResultsDisplay({ planData, selectedMode }) {
  if (!planData || !planData.plans[selectedMode]) {
    return <div>No plan data available</div>;
  }

  const modeData = planData.plans[selectedMode];
  const totals = modeData.totals;
  const cost = modeData.cost;
  const meals = modeData.meals;
  const foods = modeData.foods;

  // Calculate macro percentages
  const carbsG = totals.total_carb_g ?? 0;
  const proteinG = totals.total_protein_g ?? 0;
  const fatG = totals.total_fat_g ?? 0;

  const carbCals = carbsG * 4;
  const proteinCals = proteinG * 4;
  const fatCals = fatG * 9;
  const macroCalTotal = carbCals + proteinCals + fatCals;

  const carbPct = macroCalTotal > 0 ? (carbCals / macroCalTotal) * 100 : 0;
  const proteinPct = macroCalTotal > 0 ? (proteinCals / macroCalTotal) * 100 : 0;
  const fatPct = macroCalTotal > 0 ? (fatCals / macroCalTotal) * 100 : 0;

  // Transform meal foods to MealCard format
  const transformFoods = (foods) => {
    if (!foods) return [];
    return foods.map((f) => ({
      name: f.food,
      grams: Math.round(f.quantity_g),
      protein: Math.round(f.protein_g),
      fats: Math.round(f.fat_g ?? 0),
      carbs: Math.round(f.carb_g ?? 0),
      calories: Math.round(f.calories),
    }));
  };

  return (
    <div className="results-container">
      {/* Macro Rings Chart */}
      <MacroRingsChart
        proteinPercent={proteinPct}
        fatsPercent={fatPct}
        carbsPercent={carbPct}
      />

      {/* Meals Section */}
      <div className="meals-section">
        {meals.breakfast && (
          <MealCard
            title="Breakfast"
            totalCalories={Math.round(meals.breakfast.calories)}
            foods={transformFoods(meals.breakfast.foods)}
          />
        )}

        {meals.lunch && (
          <MealCard
            title="Lunch"
            totalCalories={Math.round(meals.lunch.calories)}
            foods={transformFoods(meals.lunch.foods)}
          />
        )}

        {meals.dinner && (
          <MealCard
            title="Dinner"
            totalCalories={Math.round(meals.dinner.calories)}
            foods={transformFoods(meals.dinner.foods)}
          />
        )}
      </div>

      {/* Micronutrients */}
      <div className="micronutrients-section">
        <h3>Micronutrients</h3>
        <div className="micronutrients-grid">
          <div>
            <strong>Iron</strong>
            <span>{totals.total_iron_mg?.toFixed(1)}mg</span>
          </div>
          <div>
            <strong>Calcium</strong>
            <span>{totals.total_calcium_mg?.toFixed(0)}mg</span>
          </div>
          <div>
            <strong>Vitamin D</strong>
            <span>{totals.total_vitamin_d_mcg?.toFixed(1)}mcg</span>
          </div>
          <div>
            <strong>Vitamin C</strong>
            <span>{totals.total_vitamin_c_mg?.toFixed(1)}mg</span>
          </div>
          <div>
            <strong>Potassium</strong>
            <span>{totals.total_potassium_mg?.toFixed(0)}mg</span>
          </div>
        </div>
      </div>

      {/* Cost */}
      <div className="cost-section">
        <h3>Cost</h3>
        <div className="cost-grid">
          <div>
            <strong>Daily Cost</strong>
            <span>Tk. {cost.total_cost_bdt?.toFixed(2)}</span>
          </div>
          <div>
            <strong>Monthly Cost</strong>
            <span>Tk. {(cost.total_cost_bdt * 30)?.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Foods List */}
      <div className="foods-list-section">
        <h3>All Foods</h3>
        <div className="foods-list">
          {foods?.map((food, idx) => (
            <div key={idx} className="food-row">
              <span>{food.food}</span>
              <span>{food.quantity_g?.toFixed(0)}g</span>
              <span>{food.calories?.toFixed(0)} kcal</span>
              <span>{food.protein_g?.toFixed(1)}g protein</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
