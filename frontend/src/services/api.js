import axios from "axios";

const API_URL = "http://localhost:5000/api";

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Generate a meal plan
 * @param {Object} userProfile - User profile data
 * @returns {Promise} Plan data with all budget modes
 */
export const generatePlan = async (userProfile) => {
  try {
    const response = await apiClient.post("/generate-plan", {
      age: userProfile.age,
      weight_kg: userProfile.weight,
      height_cm: userProfile.height,
      sex: userProfile.sex || "M",
      activity_level: userProfile.activity_level || 3,
      goal: userProfile.goal,
    });
    return response.data;
  } catch (error) {
    console.error("API Error:", error);
    throw error;
  }
};

export default apiClient;
