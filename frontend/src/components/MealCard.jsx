export default function MealCard({ title, totalCalories, foods }) {
  return (
    <div className="meal">
      <div className="meal-header">
        <span className="meal-title">{title}</span>
        <span className="meal-calories">{totalCalories} cal</span>
      </div>
      
      {foods.map((food, idx) => (
        <div key={idx} className="food-item">
          <div>
            <span className="food-name">{food.name}</span>
            <span className="food-grams"> {food.grams} g</span>
          </div>
          <span className="food-macro protein">{food.protein} g</span>
          <span className="food-macro fats">{food.fats} g</span>
          <span className="food-macro carbs">{food.carbs} g</span>
          <span className="food-cal">{food.calories} cal</span>
        </div>
      ))}
    </div>
  );
}
