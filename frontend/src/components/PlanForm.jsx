import { useState } from "react";
import AgeInput from "./AgeInput";
import WeightInput from "./WeightInput";
import HeightInput from "./HeightInput";
import GoalDropdown from "./GoalDropdown";

export default function PlanForm({ onGeneratePlan, isLoading }) {
  const [formData, setFormData] = useState({
    age: "",
    weight: "",
    height: "",
    goal: "",
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate all fields are filled
    if (!formData.age || !formData.weight || !formData.height || !formData.goal) {
      alert("Please fill in all fields");
      return;
    }

    onGeneratePlan(formData);
  };

  const updateField = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  return (
    <form onSubmit={handleSubmit}>
      <AgeInput value={formData.age} onChange={(val) => updateField("age", val)} />
      <WeightInput value={formData.weight} onChange={(val) => updateField("weight", val)} />
      <HeightInput value={formData.height} onChange={(val) => updateField("height", val)} />
      <GoalDropdown value={formData.goal} onChange={(val) => updateField("goal", val)} />
      
      <button type="submit" disabled={isLoading}>
        {isLoading ? "Generating Plan..." : "Generate Plan"}
      </button>
    </form>
  );
}
