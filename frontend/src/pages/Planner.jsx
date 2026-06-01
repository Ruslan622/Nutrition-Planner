import { useState } from "react";
import PlanForm from "../components/PlanForm";
import ResultsDisplay from "../components/ResultsDisplay";
import { generatePlan } from "../services/api";

export default function Planner() {
  const [isLoading, setIsLoading] = useState(false);
  const [planData, setPlanData] = useState(null);
  const [selectedMode, setSelectedMode] = useState("balanced");
  const [error, setError] = useState(null);

  const handleGeneratePlan = async (formData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Call backend API
      const result = await generatePlan(formData);
      setPlanData(result);
      setSelectedMode("balanced"); // Default to balanced mode
    } catch (error) {
      setError(error.message || "Error generating plan. Make sure the backend is running on port 5000");
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h1>Nutrition Planner</h1>
      
      {!planData ? (
        <>
          <PlanForm onGeneratePlan={handleGeneratePlan} isLoading={isLoading} />
          {error && <div style={{ color: "red" }}>{error}</div>}
        </>
      ) : (
        <>
          <div>
            <label>Select Budget Mode:</label>
            <select value={selectedMode} onChange={(e) => setSelectedMode(e.target.value)}>
              <option value="cheapest">Cheapest</option>
              <option value="balanced">Balanced</option>
              <option value="premium">Premium</option>
            </select>
          </div>
          
          <ResultsDisplay planData={planData} selectedMode={selectedMode} />
          
          <button onClick={() => setPlanData(null)}>← Back to Form</button>
        </>
      )}
    </div>
  );
}
