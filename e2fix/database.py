"""
E2FIX - Database Module
Handles all SQLite operations for storing history and user data.
"""

import sqlite3
import json
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "e2fix.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they don't exist."""
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS env_snapshots (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            city        TEXT NOT NULL,
            timestamp   TEXT NOT NULL,
            aqi         REAL,
            temperature REAL,
            humidity    REAL,
            heat_index  REAL,
            green_impact  REAL,
            noise_impact  REAL,
            water_stress  REAL,
            waste_pressure REAL,
            health_score  REAL,
            score_label   TEXT,
            raw_json    TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS waste_logs (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            industry_name   TEXT NOT NULL,
            timestamp       TEXT NOT NULL,
            waste_type      TEXT NOT NULL,
            quantity_kg     REAL NOT NULL,
            carbon_saved_kg REAL NOT NULL,
            carbon_credits  REAL NOT NULL,
            revenue_inr     REAL NOT NULL,
            bonus_score     REAL NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS certifications (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            industry_name   TEXT NOT NULL,
            issued_at       TEXT NOT NULL,
            health_score    REAL NOT NULL,
            total_credits   REAL NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS marketplace_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_industry TEXT NOT NULL,
            credits_amount REAL NOT NULL,
            price_per_credit REAL NOT NULL,
            status TEXT DEFAULT 'Active',
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS marketplace_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            buyer_industry TEXT NOT NULL,
            seller_industry TEXT NOT NULL,
            credits_amount REAL NOT NULL,
            total_price REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Seed default users
    count_users = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count_users == 0:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin", "Admin"))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("industry", "industry", "Industry"))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("govt", "govt", "Government"))
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("public", "public", "Public User"))

    # Seed default settings
    count_settings = c.execute("SELECT COUNT(*) FROM settings").fetchone()[0]
    if count_settings == 0:
        c.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("carbon_credit_price", "1500"))
        default_weights = json.dumps({"aqi": 0.35, "heat": 0.20, "green": 0.15, "noise": 0.10, "water": 0.10, "waste": 0.10})
        c.execute("INSERT INTO settings (key, value) VALUES (?, ?)", ("score_weights", default_weights))

    # Add status column to certifications if doesn't exist
    try:
        c.execute("ALTER TABLE certifications ADD COLUMN status TEXT DEFAULT 'Pending'")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def save_snapshot(city, data: dict):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO env_snapshots
        (city, timestamp, aqi, temperature, humidity, heat_index,
         green_impact, noise_impact, water_stress, waste_pressure,
         health_score, score_label, raw_json)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        city,
        datetime.now().isoformat(),
        data.get("aqi"),
        data.get("temperature"),
        data.get("humidity"),
        data.get("heat_index"),
        data.get("green_impact"),
        data.get("noise_impact"),
        data.get("water_stress"),
        data.get("waste_pressure"),
        data.get("health_score"),
        data.get("score_label"),
        json.dumps(data),
    ))
    conn.commit()
    conn.close()


def get_history(city=None, limit=20):
    conn = get_conn()
    c = conn.cursor()
    if city:
        rows = c.execute(
            "SELECT * FROM env_snapshots WHERE city=? ORDER BY id DESC LIMIT ?",
            (city, limit)
        ).fetchall()
    else:
        rows = c.execute(
            "SELECT * FROM env_snapshots ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def log_waste(industry, waste_type, qty_kg, carbon_saved, credits, revenue, bonus):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO waste_logs
        (industry_name, timestamp, waste_type, quantity_kg,
         carbon_saved_kg, carbon_credits, revenue_inr, bonus_score)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        industry,
        datetime.now().isoformat(),
        waste_type,
        qty_kg,
        carbon_saved,
        credits,
        revenue,
        bonus,
    ))
    conn.commit()
    conn.close()


def get_waste_logs(industry=None, limit=50):
    conn = get_conn()
    c = conn.cursor()
    if industry:
        rows = c.execute(
            "SELECT * FROM waste_logs WHERE industry_name=? ORDER BY id DESC LIMIT ?",
            (industry, limit)
        ).fetchall()
    else:
        rows = c.execute(
            "SELECT * FROM waste_logs ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_industry_totals(industry):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("""
        SELECT
            SUM(carbon_saved_kg) as total_carbon_saved,
            SUM(carbon_credits)  as total_credits,
            SUM(revenue_inr)     as total_revenue,
            COUNT(*)             as total_entries
        FROM waste_logs WHERE industry_name=?
    """, (industry,)).fetchone()
    conn.close()
    return dict(row) if row else {}


def issue_certificate(industry, health_score, total_credits):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO certifications (industry_name, issued_at, health_score, total_credits, status)
        VALUES (?,?,?,?,?)
    """, (industry, datetime.now().isoformat(), health_score, total_credits, "Pending"))
    conn.commit()
    conn.close()


def get_certificates(industry=None, status=None):
    conn = get_conn()
    c = conn.cursor()
    query = "SELECT * FROM certifications"
    params = []
    conditions = []

    if industry:
        conditions.append("industry_name=?")
        params.append(industry)
    if status:
        conditions.append("status=?")
        params.append(status)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY id DESC"
    
    rows = c.execute(query, tuple(params)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def approve_certificate(cert_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE certifications SET status='Approved' WHERE id=?", (cert_id,))
    conn.commit()
    conn.close()

def delete_record(table, record_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute(f"DELETE FROM {table} WHERE id=?", (record_id,))
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT role FROM users WHERE LOWER(username)=LOWER(?) AND password=?", (username.strip(), password.strip())).fetchone()
    conn.close()
    return row["role"] if row else None

def get_setting(key, default=None):
    conn = get_conn()
    c = conn.cursor()
    row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default

def update_setting(key, value):
    conn = get_conn()
    c = conn.cursor()
    count = c.execute("SELECT COUNT(*) FROM settings WHERE key=?", (key,)).fetchone()[0]
    if count == 0:
        c.execute("INSERT INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
    else:
        c.execute("UPDATE settings SET value=? WHERE key=?", (str(value), key))
    conn.commit()
    conn.close()

def get_company_wallet(industry_name: str) -> dict:
    """Calculate the live credit balance for a company."""
    conn = get_conn()
    
    # 1. Total credits generated
    earned = conn.execute("SELECT SUM(carbon_credits) FROM waste_logs WHERE industry_name=?", (industry_name,)).fetchone()[0] or 0.0
    
    # 2. Credits bought
    bought = conn.execute("SELECT SUM(credits_amount) FROM marketplace_transactions WHERE buyer_industry=?", (industry_name,)).fetchone()[0] or 0.0
    
    # 3. Credits sold
    sold = conn.execute("SELECT SUM(credits_amount) FROM marketplace_transactions WHERE seller_industry=?", (industry_name,)).fetchone()[0] or 0.0
    
    # 4. Credits locked in active sell orders (not yet sold)
    locked = conn.execute("SELECT SUM(credits_amount) FROM marketplace_orders WHERE seller_industry=? AND status='Active'", (industry_name,)).fetchone()[0] or 0.0
    
    # Simulated INR Wallet: Start at ₹100,000 baseline
    revenue = conn.execute("SELECT SUM(total_price) FROM marketplace_transactions WHERE seller_industry=?", (industry_name,)).fetchone()[0] or 0.0
    spent = conn.execute("SELECT SUM(total_price) FROM marketplace_transactions WHERE buyer_industry=?", (industry_name,)).fetchone()[0] or 0.0
    
    inr_balance = 100000.0 + revenue - spent
    total_credits = earned + bought - sold - locked
    
    conn.close()
    return {"balance_credits": total_credits, "balance_inr": inr_balance, "locked_credits": locked, "earned": earned, "bought": bought, "sold": sold}

def create_sell_order(seller, amount, price):
    conn = get_conn()
    conn.execute("""
        INSERT INTO marketplace_orders (seller_industry, credits_amount, price_per_credit, status, created_at)
        VALUES (?, ?, ?, 'Active', ?)
    """, (seller, amount, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def cancel_sell_order(order_id, seller):
    conn = get_conn()
    conn.execute("UPDATE marketplace_orders SET status='Cancelled' WHERE id=? AND seller_industry=? AND status='Active'", (order_id, seller))
    conn.commit()
    conn.close()

def buy_order(order_id, buyer):
    conn = get_conn()
    # Fetch order
    order = conn.execute("SELECT * FROM marketplace_orders WHERE id=? AND status='Active'", (order_id,)).fetchone()
    if not order:
        conn.close()
        return False, "Order not active or does not exist."
        
    order = dict(order)
    if order["seller_industry"] == buyer:
        conn.close()
        return False, "Cannot buy your own credits."
        
    total_price = order["credits_amount"] * order["price_per_credit"]
    
    # Update order status
    conn.execute("UPDATE marketplace_orders SET status='Sold' WHERE id=?", (order_id,))
    
    # Insert transaction
    conn.execute("""
        INSERT INTO marketplace_transactions (order_id, buyer_industry, seller_industry, credits_amount, total_price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (order_id, buyer, order["seller_industry"], order["credits_amount"], total_price, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    return True, "Successfully purchased credits!"

def get_active_orders():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM marketplace_orders WHERE status='Active' ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_transactions(limit=50):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM marketplace_transactions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]
