import { useState } from "react";

export default function MealSection({ mealType, totalCalories, foods, onAddMore }) {
  return (
    <div className="meal-section">
      {/* Header section outside the colored card block */}
      <div className="meal-header">
        <h3>{mealType}</h3>
        <span className="meal-calories">{totalCalories} Cals</span>
      </div>

      {/* The main colored container block from your layout photo */}
      <div className={`meal-card-body meal-${mealType.toLowerCase()}`}>
        <div className="meal-items">
          {foods.map((food, idx) => (
            <div key={idx} className="meal-item">
              <div className="meal-item-content">
                <h4>{food.name}</h4>
                <p>{food.serving} serving, {food.calories} calories</p>
              </div>
              <div className="meal-item-image">
                <img src={food.image} alt={food.name} />
              </div>
            </div>
          ))}
        </div>

        <button className="add-more-btn" onClick={onAddMore}>
          + Add more meal
        </button>
      </div>
    </div>
  );
}