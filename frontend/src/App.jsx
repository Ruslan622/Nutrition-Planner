import { BrowserRouter, Routes, Route } from "react-router-dom";

import Planner from "./pages/Planner";
import CustomMealPlanner from "./pages/CustomMealPlanner";

import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Planner />} />
        <Route path="/custom-plan" element={<CustomMealPlanner />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;