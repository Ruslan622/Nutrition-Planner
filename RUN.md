# Running the Nutrition Planner

## Backend (FastAPI)

### 1. Install dependencies
```bash
pip install -r docs/requirements.txt
```

### 2. Run the backend server

**Option A: Using run_api.py**
```bash
python run_api.py
```

**Option B: Using uvicorn directly**
```bash
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 5000
```

The API will be available at:
- http://localhost:5000
- OpenAPI docs: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

## Frontend (React + Vite)

### 1. Install dependencies
```bash
cd frontend
npm install
```

### 2. Run the dev server
```bash
npm run dev
```

The frontend will be available at: http://localhost:5173

---

## API Endpoints

### Generate Meal Plan
**POST** `/api/generate-plan`

Request body:
```json
{
  "age": 28,
  "weight_kg": 75,
  "height_cm": 180,
  "sex": "M",
  "activity_level": 3,
  "goal": "maintenance"
}
```

Response includes all three budget modes (cheapest, balanced, premium) with:
- Daily nutrition (calories, protein, fat, carbs, fiber)
- Micronutrients
- Cost information
- Meal breakdown (breakfast, lunch, dinner)
- All foods list

---

## Running Everything Together

**Terminal 1 (Backend):**
```bash
python run_api.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser!
