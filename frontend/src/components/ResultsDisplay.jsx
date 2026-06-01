export default function ResultsDisplay({ planData, selectedMode }) {
  if (!planData || !planData.plans[selectedMode]) {
    return <div>No plan data available</div>;
  }

  const modeData = planData.plans[selectedMode];
  const totals = modeData.totals;
  const cost = modeData.cost;
  const meals = modeData.meals;
  const foods = modeData.foods;

  return (
    <div className="results-container">
      <h2>Your {selectedMode.toUpperCase()} Plan</h2>

      {/* Daily Nutrition */}
      <div className="nutrition-section">
        <h3>Daily Nutrition</h3>
        <div className="nutrition-grid">
          <div>
            <strong>Calories:</strong> {totals.total_calories?.toFixed(0)} kcal
          </div>
          <div>
            <strong>Protein:</strong> {totals.total_protein_g?.toFixed(1)}g
          </div>
          <div>
            <strong>Fat:</strong> {totals.total_fat_g?.toFixed(1)}g
          </div>
          <div>
            <strong>Carbs:</strong> {totals.total_carb_g?.toFixed(1)}g
          </div>
          <div>
            <strong>Fiber:</strong> {totals.total_fiber_g?.toFixed(1)}g
          </div>
        </div>
      </div>

      {/* Micronutrients */}
      <div className="micronutrients-section">
        <h3>Micronutrients</h3>
        <div className="micronutrients-grid">
          <div>
            <strong>Iron:</strong> {totals.total_iron_mg?.toFixed(1)}mg
          </div>
          <div>
            <strong>Calcium:</strong> {totals.total_calcium_mg?.toFixed(0)}mg
          </div>
          <div>
            <strong>Vitamin D:</strong> {totals.total_vitamin_d_mcg?.toFixed(1)}mcg
          </div>
          <div>
            <strong>Vitamin C:</strong> {totals.total_vitamin_c_mg?.toFixed(1)}mg
          </div>
          <div>
            <strong>Potassium:</strong> {totals.total_potassium_mg?.toFixed(0)}mg
          </div>
        </div>
      </div>

      {/* Cost */}
      <div className="cost-section">
        <h3>Cost</h3>
        <div>
          <strong>Daily Cost:</strong> Tk. {cost.total_cost_bdt?.toFixed(2)}
        </div>
        <div>
          <strong>Monthly Cost:</strong> Tk. {(cost.total_cost_bdt * 30)?.toFixed(2)}
        </div>
      </div>

      {/* Meals */}
      <div className="meals-section">
        <h3>Meal Breakdown</h3>

        {/* Breakfast */}
        {meals.breakfast && (
          <div className="meal">
            <h4>🌅 Breakfast</h4>
            <p>
              <strong>{meals.breakfast.calories?.toFixed(0)} kcal</strong> ({((meals.breakfast.calories / totals.total_calories) * 100)?.toFixed(0)}%)
            </p>
            <p><strong>Protein:</strong> {meals.breakfast.protein_g?.toFixed(1)}g</p>
            <div className="foods">
              {meals.breakfast.foods?.map((food, idx) => (
                <div key={idx} className="food-item">
                  • {food.food}: {food.quantity_g?.toFixed(0)}g
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Lunch */}
        {meals.lunch && (
          <div className="meal">
            <h4>🍽️ Lunch</h4>
            <p>
              <strong>{meals.lunch.calories?.toFixed(0)} kcal</strong> ({((meals.lunch.calories / totals.total_calories) * 100)?.toFixed(0)}%)
            </p>
            <p><strong>Protein:</strong> {meals.lunch.protein_g?.toFixed(1)}g</p>
            <div className="foods">
              {meals.lunch.foods?.map((food, idx) => (
                <div key={idx} className="food-item">
                  • {food.food}: {food.quantity_g?.toFixed(0)}g
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Dinner */}
        {meals.dinner && (
          <div className="meal">
            <h4>🍲 Dinner</h4>
            <p>
              <strong>{meals.dinner.calories?.toFixed(0)} kcal</strong> ({((meals.dinner.calories / totals.total_calories) * 100)?.toFixed(0)}%)
            </p>
            <p><strong>Protein:</strong> {meals.dinner.protein_g?.toFixed(1)}g</p>
            <div className="foods">
              {meals.dinner.foods?.map((food, idx) => (
                <div key={idx} className="food-item">
                  • {food.food}: {food.quantity_g?.toFixed(0)}g
                </div>
              ))}
            </div>
          </div>
        )}
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
