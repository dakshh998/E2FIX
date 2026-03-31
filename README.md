# 🌿 E2FIX: Environment Evaluation & Fixing System

E2FIX is an interactive environmental evaluation and action platform built with Streamlit. It offers a comprehensive system for monitoring real-world environmental health across global coordinates and provides an interactive "Carbon Credit Marketplace" where industries can simulate logging waste and trading emission credits.

**Project Status**: Developed for the B.Tech First Year EVS Project at IILM University.

## ✨ Key Features

*   **Global Environmental Discovery:** Search for any location worldwide or simply click on the interactive Folium map to pinpoint coordinates and analyze the environmental profile exactly where you clicked.
*   **Comprehensive Health Scoring:** Pulls live Air Quality Index (AQI) from WAQI and Weather data from OpenWeather. Computes multi-factor environmental indices (Green Impact, Water Stress, Noise Pollution, etc.) into a master "Health Score".
*   **Smart Action Plan Engine:** Generates localized, context-aware action steps (e.g. issues warnings on high temp, triggers waste drives on high pollution) based on real-time data metrics.
*   **Carbon Credit Marketplace:** A full simulation of a localized emission trading economy:
    *   **🏭 Log Waste:** Industries can track managed waste materials and log equivalent CO2 reduction.
    *   **💳 Live Wallets:** The platform tracks generated carbon credits and simulated INR balances uniquely per company.
    *   **💱 Trading Floor:** Companies can list credits on an open market and securely purchase credits listed by other participating industries.
*   **Green Certificates:** Government or Admin accounts can dynamically monitor high-performing industries and auto-generate certified green compliance PDFs.
*   **Forecasting & Analytics:** Visual charts (via Plotly) for long-term tracking of city metrics and simple predictive indexing.

## 🚀 Live Demo Configuration

Out of the box, **E2FIX runs in Demo Mode**. The core metrics and API responses will be simulated with realistic deterministic values so anyone can run the app without spending hours registering API keys. However, for real-world live tracking, you will need to add your free WAQI and OpenWeatherMap tokens inside `config.py`.

## 🛠️ Required Stack & Installation

This project is perfectly tailored for deployment on Streamlit Community Cloud. Follow these steps to set it up locally:

### 1. Prerequisites
Make sure Python 3.9+ is installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Core dependencies include: `streamlit`, `plotly`, `pandas`, `requests`, `folium`, `streamlit-folium`, and `fpdf2`)*

### 3. Run the App
```bash
streamlit run app.py
```
*(If on Windows, you can simply run the provided `run_e2fix.bat` script).*

## 🔒 Authentication Levels

The app has basic role-based access for demonstration purposes. Use the credentials below to log in:
*   **Admin Access:** `admin` / `admin` *(Access to all modules)*
*   **Industry Access:** `industry` / `industry` *(Limits user to Waste & Marketplace functionality)*
*   **Govt Access:** `govt` / `govt` *(Auditing and Analytics panels)*
*   **Public Access:** `public` / `public` *(Dashboard viewing only)*

## 📁 Repository Structure

If you are uploading this to Streamlit Community Cloud (via GitHub), you **only** need exactly these core files:
*   `app.py`  **(Main Runner)**
*   `engine.py` *(Core computation and API/Geocoding logic)*
*   `database.py` *(SQLite3 schemas and marketplace ledger system)*
*   `config.py` *(Environment thresholds and API Keys)*
*   `reports.py` *(Automated PDF Certificate Generation)*
*   `requirements.txt` *(Deployment requirements)*

*(You do NOT need to push your local `__pycache__` folders, `.pdf` exports, or your `e2fix.db` database. Streamlit will auto-init an empty database upon boot).*
