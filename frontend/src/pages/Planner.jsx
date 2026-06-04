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
      const result = await generatePlan(formData);
      setPlanData(result);
      setSelectedMode("balanced");
    } catch (error) {
      setError(error.message || "Error generating plan. Make sure the backend is running on port 5000");
      console.error("Error:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="planner-page">
      <div className="planner-header">
        <h1>Nutrition Planner</h1>
        <p style={{ color: '#666', marginTop: '10px', fontSize: '1.1em' }}>
          Create personalized meal plans based on your goals
        </p>
      </div>
      
      {!planData ? (
        <div className="form-container">
          <PlanForm onGeneratePlan={handleGeneratePlan} isLoading={isLoading} />
          {error && <div className="error-message">{error}</div>}
        </div>
      ) : (
        <>
          <div className="mode-selector">
            <label htmlFor="mode-select">Select Budget Mode:</label>
            <select 
              id="mode-select"
              value={selectedMode} 
              onChange={(e) => setSelectedMode(e.target.value)}
            >
              <option value="cheapest">Cheapest</option>
              <option value="balanced">Balanced</option>
              <option value="premium">Premium</option>
            </select>
          </div>
          
          <ResultsDisplay planData={planData} selectedMode={selectedMode} />
          
          <button className="back-button" onClick={() => setPlanData(null)}>
            Back to Form
          </button>
        </>
      )}
    </div>
  );
}
