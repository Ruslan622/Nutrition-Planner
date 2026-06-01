export default function ResultsDisplay({ planData, selectedMode }) {
  if (!planData || !planData.plans[selectedMode]) {
    return <div>No plan data available</div>;
  }

  const modeData = planData.plans[selectedMode];
  const totals = modeData.totals;
  const cost = modeData.cost;
  const meals = modeData.meals;
  const foods = modeData.foods;
  const target = planData.targets.target_calories;

  // Macro donut: each segment is % of total macro calories
  const calories = totals.total_calories ?? 0;
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

  const r = 45;
  const circumference = 2 * Math.PI * r;
  const gap = 2; // small visual separation between segments

  const carbLenRaw = (carbPct / 100) * circumference;
  const proteinLenRaw = (proteinPct / 100) * circumference;
  const fatLenRaw = (fatPct / 100) * circumference;

  const carbLen = Math.max(0, carbLenRaw - gap);
  const proteinLen = Math.max(0, proteinLenRaw - gap);
  const fatLen = Math.max(0, fatLenRaw - gap);

  const carbDasharray = `${carbLen} ${circumference - carbLen}`;
  const proteinDasharray = `${proteinLen} ${circumference - proteinLen}`;
  const fatDasharray = `${fatLen} ${circumference - fatLen}`;

  const carbDashoffset = 0;
  const proteinDashoffset = -(carbLenRaw);
  const fatDashoffset = -(carbLenRaw + proteinLenRaw);

  return (
    <div className="results-container">
      <h2>Your {selectedMode.toUpperCase()} Plan</h2>

      {/* Macro Chart */}
      <div className="macro-chart-container">
        <div className="chart-wrapper">
          <svg viewBox="0 0 120 120" className="macro-chart-svg">
            {/* Background circle */}
            <circle cx="60" cy="60" r="45" className="chart-bg" />

            {/* Segments (carb -> protein -> fat) */}
            <circle
              cx="60"
              cy="60"
              r="45"
              className="chart-segment carbs"
              style={{ strokeDasharray: carbDasharray, strokeDashoffset: carbDashoffset }}
            />
            <circle
              cx="60"
              cy="60"
              r="45"
              className="chart-segment protein"
              style={{ strokeDasharray: proteinDasharray, strokeDashoffset: proteinDashoffset }}
            />
            <circle
              cx="60"
              cy="60"
              r="45"
              className="chart-segment fat"
              style={{ strokeDasharray: fatDasharray, strokeDashoffset: fatDashoffset }}
            />
          </svg>

          {/* Center text */}
          <div className="chart-center">
            <div className="calories-display">{calories.toFixed(0)}</div>
            <div className="calories-label">/ {target.toFixed(0)} kcal</div>
          </div>
        </div>

        {/* Macro breakdown */}
        <div className="macro-breakdown">
          <div className="macro-item carbs">
            <span className="macro-label">Carbs</span>
            <span className="macro-value">
              {carbsG.toFixed(0)}g ({Math.round(carbPct)}%)
            </span>
          </div>
          <div className="macro-item protein">
            <span className="macro-label">Protein</span>
            <span className="macro-value">
              {proteinG.toFixed(0)}g ({Math.round(proteinPct)}%)
            </span>
          </div>
          <div className="macro-item fat">
            <span className="macro-label">Fat</span>
            <span className="macro-value">
              {fatG.toFixed(0)}g ({Math.round(fatPct)}%)
            </span>
          </div>
        </div>
      </div>

      {/* Micronutrients */}
      <div className="micronutrients-section">
        <h3>🧬 Micronutrients</h3>
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
        <h3>💰 Cost</h3>
        <div>
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

      {/* Meals */}
      <div className="meals-section">
        <h3>🍽️ Meal Breakdown</h3>

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
                  <span>• {food.food}</span>
                  <span>{food.quantity_g?.toFixed(0)}g</span>
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
                  <span>• {food.food}</span>
                  <span>{food.quantity_g?.toFixed(0)}g</span>
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
                  <span>• {food.food}</span>
                  <span>{food.quantity_g?.toFixed(0)}g</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Foods List */}
      <div className="foods-list-section">
        <h3>📋 All Foods</h3>
        <div className="foods-list">
          {foods?.map((food, idx) => (
            <div key={idx} className="food-row">
              <span>{food.food}</span>
              <span>{food.quantity_g?.toFixed(0)}g</span>
              <span>{food.calories?.toFixed(0)} kcal</span>
              <span>{food.protein_g?.toFixed(1)}g</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
