import { useState } from "react";
import MealSection from "../components/MealSection";

export default function CustomMealPlanner() {
  const [meals, setMeals] = useState({
    breakfast: [
      { name: "Oatmeal", serving: "1.0", calories: 210, image: "https://via.placeholder.com/80?text=Oatmeal" },
      { name: "Truroots Organic", serving: "1.0", calories: 138, image: "https://via.placeholder.com/80?text=Organic" },
      { name: "Orange Juice", serving: "1.0", calories: 50, image: "https://via.placeholder.com/80?text=OJ" },
    ],
    lunch: [
      { name: "BBQ Meat", serving: "1.0", calories: 210, image: "https://via.placeholder.com/80?text=BBQ" },
      { name: "Rice with Chicken", serving: "1.0", calories: 138, image: "https://via.placeholder.com/80?text=Chicken" },
    ],
    dinner: [
      { name: "Grilled Fish", serving: "1.0", calories: 180, image: "https://via.placeholder.com/80?text=Fish" },
    ],
  });

  // Function to calculate total calories for a given meal array
  const calculateTotalCalories = (foodArray) => {
    return foodArray.reduce((sum, food) => sum + food.calories, 0);
  };

  const handleAddMoreMeal = (mealType) => {
    // Prompting for basic input just to show dynamic state update. 
    // In production, you would trigger a beautiful modal form here!
    const name = prompt(`Enter food name for ${mealType}:`);
    if (!name) return;

    const calories = parseInt(prompt("Enter calories:"), 10) || 0;
    const serving = prompt("Enter serving amount (e.g., 1.0):") || "1.0";

    const newFoodItem = {
      name,
      serving,
      calories,
      image: "https://via.placeholder.com/80?text=Food", // Default placeholder
    };

    setMeals((prevMeals) => ({
      ...prevMeals,
      [mealType]: [...prevMeals[mealType], newFoodItem],
    }));
  };

  return (
    <div className="custom-meal-planner">
      <div className="custom-meal-header">
        <h1>Meal Plan</h1>
        <div className="header-icon">👤</div>
      </div>

      <div className="meals-container">
        {/* Breakfast */}
        <MealSection
          mealType="Breakfast"
          totalCalories={calculateTotalCalories(meals.breakfast)}
          foods={meals.breakfast}
          onAddMore={() => handleAddMoreMeal("breakfast")}
        />

        {/* Lunch */}
        <MealSection
          mealType="Lunch"
          totalCalories={calculateTotalCalories(meals.lunch)}
          foods={meals.lunch}
          onAddMore={() => handleAddMoreMeal("lunch")}
        />

        {/* Dinner */}
        <MealSection
          mealType="Dinner"
          totalCalories={calculateTotalCalories(meals.dinner)}
          foods={meals.dinner}
          onAddMore={() => handleAddMoreMeal("dinner")}
        />
      </div>
    </div>
  );
}