# Online Product Recommendation and Comparison System
## Dissertation Context Guide

This document provides a comprehensive breakdown of the technical architecture, algorithms, and development process used to build the **RecommendX** system. This context is designed to assist you in writing the chapters of your final year dissertation.

---

### 1. Project Overview & Architecture
The system is built as a **Monolithic Web Application** following the MVC (Model-View-Controller) paradigm, although adapted for modern API-first development.

* **Backend Framework:** Python with **FastAPI**. FastAPI was chosen for its high performance, automatic API documentation (Swagger UI), and asynchronous routing capabilities.
* **Frontend:** Vanilla HTML5, CSS3, and JavaScript, styled with **Bootstrap 5.3** and **Bootstrap Icons** for a responsive, modern Dark Mode interface.
* **Database:** **SQLite**. Chosen for its serverless nature and ease of deployment for a standalone application. Data is managed via raw SQL and `sqlite3` driver in Python for explicit control over queries.
* **Templating:** FastAPI's `Jinja2Templates` is used to serve the initial HTML pages, while dynamic data (products, reviews, recommendations) is fetched asynchronously via JavaScript `fetch` API calls to the FastAPI backend.

---

### 2. The Database Schema
The relational database (`products.db`) consists of four core tables:

1. **`products`**: Stores all product metadata (Name, Category, Price, Specifications like RAM/Storage/Battery, and an automatically calculated `average_rating`).
2. **`users`**: Stores user profiles (Username, Email) required for the collaborative filtering engine algorithm.
3. **`ratings`**: A junction table linking `users` to `products` with a 1-5 numerical score. This is exclusively used to build the collaborative filtering matrix.
4. **`reviews`**: Stores detailed text-based user feedback, including the associated product, user name, text review, 1-5 star rating, and timestamp.

---

### 3. Recommendation Engine Architecture
The core innovation of the project is a **Hybrid Recommendation Engine** that combines multiple data science approaches without relying on external pre-trained "black box" machine learning models. Everything is computed mathematically from scratch in Python.

#### A. Content-Based Filtering (`engine/content_based.py`)
This engine recommends products that are *similar to the one the user is currently viewing*.
* **Feature Engineering:** It extracts categorical features (e.g., Category, RAM) and converts them into numerical vectors using **One-Hot Encoding**.
* **Similarity Metric:** It calculates the **Cosine Similarity** between the target product's vector and all other products in the database. 
* **Result:** It accurately identifies products sharing identical or highly similar technical specifications, enforcing a ~70% precision rate for matching item categories.

#### B. Collaborative Filtering (`engine/collaborative.py`)
This engine recommends products based on *user behavior and consensus*. It utilizes a **User-Based K-Nearest Neighbors (KNN)** approach.
* **Matrix Building:** It constructs a highly sparse "User-Item Matrix" mapping every user to the ratings they gave specific products.
* **Neighbor Identification:** Using **Cosine Similarity**, it compares the target user's rating vector against all other users to find the closest "Neighbors" (people with similar tastes).
* **Prediction:** It aggregates the ratings from the top 10 most similar users to recommend items the target user hasn't seen yet.

#### C. The Hybrid Engine (`engine/hybrid.py`)
This is the master algorithm that blends the two standalone engines to overcome their individual weaknesses (such as the "Cold Start" problem in collaborative filtering).
* **Normalization:** It normalizes the scores from both engines ensuring they operate on the same mathematical scale (0 to 1).
* **Weighted Combination:** It adds the scores together to form a baseline hybrid score.
* **Dynamic Review Boosting:** Unlike traditional engines, this system incorporates real-time sentiment by directly boosting the recommendation score based on the product's live `average_rating` calculated from the review system. Highly-rated products are artificially buoyed to the top.

---

### 4. Custom Review & Sentiment Generation
To ensure the system could be properly evaluated at defense without an active user base, a highly sophisticated synthetic data generation script (`data/seed_data.py`) was developed.

* **Stratified Sourcing:** The system mimics a real e-commerce environment by housing 44 unique products spread across 9 distinct categories (Electronics, Appliances, Baby stuff, etc.).
* **Contextual Reviews:** 440 unique, linguistically diverse reviews were generated using a rotating pool algorithm. A review for a Gas Cooker specifically mentions "flame intensity", while a Cradle review mentions "comfort and safety".
* **Strict Sentiment-to-Star Mapping:** The algorithm guarantees data integrity. Positive linguistic phrasing ("exceptional", "efficient") is strictly hardcoded to 4 and 5-star ratings, while negative phrasing ("slow delivery", "low build quality") maps exclusively to 1 and 2 stars. 

---

### 5. Key System Features
* **Dark Mode UI:** A professional, low-eye-strain interface utilizing global CSS variables for dynamic color mapping based on product category.
* **Side-by-Side Comparison:** A dedicated module (`compare.html`) allowing users to select up to 3 products across any category, dynamically aligning their specifications into a responsive table, and highlighting the mathematically "Best Value" and "Highest Rated" options.
* **User-Generated Content:** A complete API loop allowing users to submit new products to the database manually (`/add-product`) and leave new reviews on existing products, which instantly triggers a recalculation of the product's overall rating and dynamically alters its positioning in the recommendation algorithms.

---

### 6. Mathematical Evaluation & Accuracy
The recommendation engine was mathematically evaluated using a standard 80/20 Train/Test Data Split:
* **RMSE (Root Mean Square Error):** `0.9628` (meaning rating predictions are off by less than 1 star on average).
* **MAE (Mean Absolute Error):** `0.8325`
* **Hit Rate @ 10:** `24.44%` (meaning 1 out of 4 times, the engine successfully places an unknown "liked" product into a user's Top 10 recommendations).
