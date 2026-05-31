# config.py
# Central configuration for NutriBudget BD
# All constants, food definitions, and scraper targets live here.

# ─── Activity multipliers (PAL values — WHO/FAO standard) ───────────────────
ACTIVITY_LEVELS = {
    "1": {"label": "Sedentary",        "description": "Desk job, no exercise",           "factor": 1.2},
    "2": {"label": "Lightly active",   "description": "Light exercise 1–3 days/week",    "factor": 1.375},
    "3": {"label": "Moderately active","description": "Moderate exercise 3–5 days/week", "factor": 1.55},
    "4": {"label": "Very active",      "description": "Hard exercise 6–7 days/week",     "factor": 1.725},
    "5": {"label": "Extra active",     "description": "Physical job + daily training",   "factor": 1.9},
}

# ─── Goal definitions ────────────────────────────────────────────────────────
GOALS = {
    "1": {
        "key":         "maintenance",
        "label":       "Maintenance",
        "description": "Eat at TDEE — sustain current weight",
        "calorie_delta": 0,          # kcal added to TDEE
        "protein_per_kg": 1.6,       # g protein per kg bodyweight (ISSN minimum)
        "fat_pct":     0.25,         # 25% of calories from fat
    },
    "2": {
        "key":         "loss",
        "label":       "Fat Loss",
        "description": "500 kcal deficit — ~0.5 kg fat loss per week",
        "calorie_delta": -500,
        "protein_per_kg": 2.2,       # Higher protein spares muscle during cut (ISSN)
        "fat_pct":     0.25,
    },
    "3": {
        "key":         "gain",
        "label":       "Muscle Gain",
        "description": "300 kcal surplus — lean bulk for muscle growth",
        "calorie_delta": +300,
        "protein_per_kg": 2.0,       # 1.6–2.2 g/kg for hypertrophy (ISSN 2017)
        "fat_pct":     0.25,
    },
}

# ─── Food definitions ────────────────────────────────────────────────────────
# Macros are per 100g (cooked where applicable).
# Sources: USDA FoodData Central, FAO/INFOODS South Asia tables.
# price_per_kg / price_per_piece are FALLBACK values if scraping fails.
# unit: "g" | "piece" | "ml"
# grams_each: for piece-based foods, grams per piece (used for macro calc)

FOODS = {
    "rice": {
        "name":        "Rice (cooked)",
        "unit":        "g",
        "cal_per_100": 130,
        "pro_per_100": 2.7,
        "fat_per_100": 0.3,
        "carb_per_100":28.0,
        "fallback_price_per_kg": 70,     # BDT/kg (cooked, approximate)
        "scrape_query": "minuket rice",  # search term for scrapers
    },
    "bread": {
        "name":        "Bread / Roti (local)",
        "unit":        "g",
        "cal_per_100": 250,
        "pro_per_100": 8.0,
        "fat_per_100": 1.5,
        "carb_per_100":50.0,
        "fallback_price_per_kg": 60,
        "scrape_query": "bread loaf",
    },
    "egg": {
        "name":        "Egg (whole)",
        "unit":        "piece",
        "grams_each":  60,             # ~60g per large egg
        "cal_per_100": 155,
        "pro_per_100": 13.0,
        "fat_per_100": 11.0,
        "carb_per_100":1.1,
        "fallback_price_per_piece": 12,  # BDT per egg
        "scrape_query": "eggs",
    },
    "lentil": {
        "name":        "Lentil / Masoor Daal (cooked)",
        "unit":        "g",
        "cal_per_100": 116,
        "pro_per_100": 9.0,
        "fat_per_100": 0.4,
        "carb_per_100":20.0,
        "fallback_price_per_kg": 130,
        "scrape_query": "masoor dal",
    },
    "chickpea": {
        "name":        "Chhola / Chickpea (cooked)",
        "unit":        "g",
        "cal_per_100": 164,
        "pro_per_100": 8.9,
        "fat_per_100": 2.6,
        "carb_per_100":27.0,
        "fallback_price_per_kg": 120,
        "scrape_query": "chola boot",
    },
    "chicken": {
        "name":        "Chicken breast (boneless, cooked)",
        "unit":        "g",
        "cal_per_100": 165,
        "pro_per_100": 31.0,
        "fat_per_100": 3.6,
        "carb_per_100":0.0,
        "fallback_price_per_kg": 320,
        "scrape_query": "chicken breast boneless",
    },
    "beef": {
        "name":        "Beef (lean, cooked)",
        "unit":        "g",
        "cal_per_100": 250,
        "pro_per_100": 26.0,
        "fat_per_100": 17.0,
        "carb_per_100":0.0,
        "fallback_price_per_kg": 700,
        "scrape_query": "beef",
    },
    "fish": {
        "name":        "Tilapia fish (cooked)",
        "unit":        "g",
        "cal_per_100": 96,
        "pro_per_100": 20.0,
        "fat_per_100": 1.7,
        "carb_per_100":0.0,
        "fallback_price_per_kg": 200,
        "scrape_query": "tilapia fish",
    },
    "milk": {
        "name":        "Milk (full fat)",
        "unit":        "ml",
        "cal_per_100": 61,
        "pro_per_100": 3.2,
        "fat_per_100": 3.3,
        "carb_per_100":4.8,
        "fallback_price_per_litre": 75,
        "scrape_query": "fresh milk",
    },
}

# ─── Daily food portions per goal ────────────────────────────────────────────
# These are the BASE portions that the planner uses as a starting point.
# The planner scales them to hit calorie + protein targets.
# Format: { food_key: quantity }
# Quantities are in grams (g) / ml / pieces depending on food unit.

BASE_PLANS = {
    "maintenance": {
        "rice":     250,   # g cooked
        "bread":     80,   # g
        "egg":        2,   # pieces
        "lentil":   100,   # g cooked
        "chicken":  150,   # g cooked
        "fish":     100,   # g cooked
        "milk":     300,   # ml
    },
    "loss": {
        "rice":     150,   # reduced carbs
        "egg":        2,
        "lentil":    80,
        "chickpea":  80,
        "chicken":  180,   # higher protein
        "fish":     150,
        "milk":     250,
    },
    "gain": {
        "rice":     350,   # more carbs for energy
        "bread":     80,
        "egg":        3,   # more eggs
        "lentil":   100,
        "chicken":  200,   # more protein
        "fish":     100,
        "beef":      80,   # added beef for variety
        "milk":     400,
    },
}

# ─── Scraper settings ─────────────────────────────────────────────────────────
CACHE_FILE    = "data/prices_cache.json"
CACHE_MAX_AGE = 24 * 60 * 60  # 24 hours in seconds — re-scrape after this

CHALDAL_BASE  = "https://chaldal.com"
SHWAPNO_BASE  = "https://www.shwapno.com"

SCRAPER_TIMEOUT  = 15   # seconds per page
SCRAPER_HEADLESS = True