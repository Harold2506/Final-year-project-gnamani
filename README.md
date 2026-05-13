# Online Product Recommendation and Comparison System

> **Final Year Project** — A hybrid machine learning system that helps users overcome *information overload* when shopping for electronics online.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [How This System Solves It](#how-this-system-solves-it)
3. [Technologies Used](#technologies-used)
4. [Project Structure](#project-structure)
5. [How to Run](#how-to-run)
6. [API Endpoints](#api-endpoints)
7. [Recommendation Engine Explained](#recommendation-engine-explained)
8. [Screenshots](#screenshots)

---

## Problem Statement

The rapid growth of e-commerce has led to a phenomenon known as **information overload** — users are presented with thousands of product options but lack the tools to efficiently narrow down their choices. This cognitive burden results in:

- **Decision fatigue**: Users abandon purchases because they cannot compare options easily.
- **Poor purchasing decisions**: Without personalized guidance, users may choose products that do not match their preferences or needs.
- **Reduced user satisfaction**: Generic product listings fail to surface items that are relevant to individual users.

This project directly addresses these challenges by implementing a **hybrid recommendation engine** and a **side-by-side comparison tool** for electronics (smartphones and laptops).

---

## How This System Solves It

| Problem | Solution |
|---|---|
| Too many products to browse | **Content-Based Filtering** surfaces products similar to the one a user is viewing, based on shared attributes (RAM, Category). |
| No personalization | **Collaborative Filtering** identifies users with similar tastes and recommends what they liked. |
| Hard to compare specifications | **Comparison Tool** lets users select 2–3 products and view specs side-by-side in a clean table. |
| Conflicting recommendation methods | **Hybrid Engine** combines both approaches using a weighted score (α = 0.5) for balanced, accurate results. |

---

## Technologies Used

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend Framework | **FastAPI** (Python) | High-performance REST API with automatic Swagger docs |
| Database | **SQLite** (via `sqlite3`) | Lightweight, file-based SQL storage — no server required |
| Recommendation Math | **Cosine Similarity** (pure Python) | Core similarity metric for both filtering methods |
| Frontend | **HTML5 / CSS3 / JavaScript** | Dynamic, responsive user interface |
| Frontend Framework | **Bootstrap 5** | Professional layout, components, and responsiveness |
| Typography | **Inter** (Google Fonts) | Clean, modern, academic-feel font |
| Icons | **Bootstrap Icons** | Consistent iconography throughout the UI |
| Data Generation | **Python `csv` + `random`** | Synthetic dataset creation with no external dependencies |

---

## Project Structure

```
recommendation_system/
│
├── app/                          # Backend application
│   ├── main.py                   # FastAPI entry point (serves pages + API)
│   ├── database.py               # SQLite connection and query helpers
│   ├── schemas.py                # Pydantic validation models
│   ├── models.py                 # Database table definitions
│   ├── __init__.py
│   └── routes/
│       ├── recommendations.py    # API endpoints (products, recommend, compare)
│       └── __init__.py
│
├── engine/                       # Recommendation engine (pure Python)
│   ├── engine_utils.py           # Cosine Similarity formula + CSV loader
│   ├── content_based.py          # Content-Based Filtering logic
│   ├── collaborative.py          # Collaborative Filtering logic
│   ├── hybrid.py                 # Hybrid combination of both methods
│   └── __init__.py
│
├── templates/                    # Frontend HTML pages (served by FastAPI)
│   ├── index.html                # Home — product grid + recommendations
│   ├── product_detail.html       # Product Detail — specs + similar products
│   └── compare.html              # Comparison — side-by-side table
│
├── static/
│   └── css/
│       └── style.css             # Custom stylesheet (Blue/White/Grey palette)
│
├── data/                         # Data layer
│   ├── generate_data.py          # Script to create synthetic CSV datasets
│   ├── seed_data.py              # Script to populate SQLite from CSVs
│   ├── products.csv              # 68 electronics products
│   ├── user_ratings.csv          # 500 user-product interactions
│   └── products.db               # SQLite database (auto-generated)
│
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## How to Run

### Prerequisites
- **Python 3.10+** installed on your system.
- **pip** (Python package manager).

### Step-by-Step

```bash
# 1. Clone or download the project
cd recommendation_system

# 2. Install dependencies
pip install fastapi uvicorn

# 3. Generate synthetic data (if not already present)
python data/generate_data.py

# 4. Seed the SQLite database from the CSVs
python data/seed_data.py

# 5. Start the server
uvicorn app.main:app --reload
```

### Then open your browser:

| URL | Description |
|-----|-------------|
| `http://localhost:8000` | Home page (product catalog + recommendations) |
| `http://localhost:8000/product?id=101` | Product detail page |
| `http://localhost:8000/compare?ids=101,106,137` | Comparison page |
| `http://localhost:8000/docs` | Interactive API documentation (Swagger UI) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/products` | List all products |
| `GET` | `/api/products/{id}` | Get a single product by ID |
| `POST` | `/api/recommend` | Get hybrid recommendations (body: `user_id`, `last_product_id`, `top_n`) |
| `GET` | `/api/compare?product_ids=101,102` | Compare 2–3 products side-by-side |
| `GET` | `/health` | Server health check |

---

## Recommendation Engine Explained

### 1. Content-Based Filtering (`engine/content_based.py`)
- Converts each product's **Category** and **RAM** into a binary feature vector using **one-hot encoding**.
- Computes **Cosine Similarity** between the target product and all others.
- Returns the top-N most similar products.

### 2. Collaborative Filtering (`engine/collaborative.py`)
- Builds a **User-Item Rating Matrix** from the `user_ratings.csv` data.
- Converts each user's ratings into a fixed-length vector.
- Finds the **top-10 most similar users** using Cosine Similarity.
- Aggregates the products those users liked (weighted by similarity) and recommends unseen items.

### 3. Hybrid Engine (`engine/hybrid.py`)
- Combines scores from both methods:

```
Final Score = α × Content Score + (1 - α) × Normalized Collab Score
```

- Default **α = 0.5** gives equal weight to both approaches.
- Returns a single, merged recommendation list sorted by combined score.

### Core Formula: Cosine Similarity (`engine/engine_utils.py`)

```
Similarity(A, B) = (A · B) / (‖A‖ × ‖B‖)
```

Where `A · B` is the dot product and `‖A‖` is the Euclidean norm. This is implemented from scratch in pure Python for full transparency during the project defense.

---

## Screenshots

### Home Page
The home page displays personalized recommendations and a filterable product catalog.

### Product Detail
Each product page shows full specifications and a "Similar Products" section.

### Comparison
Users can select 2–3 products and view a side-by-side table with green highlights on the best values, plus a "Quick Verdict" summary.

---

## License

This project was built for academic purposes as a Final Year Project.

© 2026 — Online Product Recommendation and Comparison System.
