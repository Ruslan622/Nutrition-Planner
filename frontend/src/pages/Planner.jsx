import { useState } from "react";
import PlanForm from "../components/PlanForm";

export default function Planner() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleGeneratePlan = async (formData) => {
    setIsLoading(true);
    
    try {
      // TODO: Connect to backend API
      console.log("Form data:", formData);
      
      // Placeholder - will connect to backend later
      console.log("Backend connection coming soon...");
      
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1>Nutrition Planner</h1>
      <PlanForm onGeneratePlan={handleGeneratePlan} isLoading={isLoading} />
      {result && <div>{JSON.stringify(result)}</div>}
    </div>
  );
}
