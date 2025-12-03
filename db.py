import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / 'data.db'

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        calories REAL NOT NULL
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        name TEXT NOT NULL,
        duration REAL NOT NULL,
        calories REAL NOT NULL
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS weights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        week TEXT NOT NULL,
        date TEXT NOT NULL,
        weight REAL NOT NULL
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS completed_days (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        calories_eaten REAL,
        calories_burned REAL,
        net_calories REAL,
        daily_goal REAL,
        percent_reached INTEGER,
        created_at TEXT DEFAULT (datetime('now'))
    )
    ''')

    conn.commit()
    conn.close()

# Meals
def add_meal(date, description, calories):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO meals (date, description, calories) VALUES (?,?,?)', (date, description, calories))
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid

def get_meals_for_date(date):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT description, calories FROM meals WHERE date = ? ORDER BY id', (date,))
    rows = cur.fetchall()
    conn.close()
    items = [{'description': r['description'], 'calories': r['calories']} for r in rows]
    total = sum(r['calories'] for r in rows)
    return items, total

# Workouts
def add_workout(date, name, duration, calories):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('INSERT INTO workouts (date, name, duration, calories) VALUES (?,?,?,?)', (date, name, duration, calories))
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid

def get_workouts_for_date(date):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT name, duration, calories FROM workouts WHERE date = ? ORDER BY id', (date,))
    rows = cur.fetchall()
    conn.close()
    items = [{'name': r['name'], 'duration': r['duration'], 'calories': r['calories']} for r in rows]
    total = sum(r['calories'] for r in rows)
    return items, total

# Weights
def add_weight(date, weight):
    # store by ISO week key
    try:
        dt = datetime.fromisoformat(date)
    except Exception:
        dt = datetime.utcnow()
    iso_year, iso_week, _ = dt.isocalendar()
    key = f"{iso_year}-W{iso_week:02d}"
    conn = get_conn()
    cur = conn.cursor()
    # Upsert by week: if exists update, else insert
    cur.execute('SELECT id FROM weights WHERE week = ?', (key,))
    row = cur.fetchone()
    if row:
        cur.execute('UPDATE weights SET date = ?, weight = ? WHERE week = ?', (date, weight, key))
    else:
        cur.execute('INSERT INTO weights (week, date, weight) VALUES (?,?,?)', (key, date, weight))
    conn.commit()
    conn.close()
    return key

def get_weights():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT week, weight FROM weights ORDER BY week')
    rows = cur.fetchall()
    conn.close()
    return [{'week': r['week'], 'weight': r['weight']} for r in rows]

# Completed days
def add_completed_day(date, calories_eaten, calories_burned, net_calories, daily_goal, percent_reached):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('''INSERT INTO completed_days (date, calories_eaten, calories_burned, net_calories, daily_goal, percent_reached) VALUES (?,?,?,?,?,?)''',
                (date, calories_eaten, calories_burned, net_calories, daily_goal, percent_reached))
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid

def get_completed_day(date):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('SELECT date, calories_eaten, calories_burned, net_calories, daily_goal, percent_reached FROM completed_days WHERE date = ? ORDER BY id DESC LIMIT 1', (date,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def clear_all_data():
    """Delete all user data from the database tables (meals, workouts, weights, completed_days).
    Used for resetting the app during development or when the user requests a full reset.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute('DELETE FROM meals')
    cur.execute('DELETE FROM workouts')
    cur.execute('DELETE FROM weights')
    cur.execute('DELETE FROM completed_days')
    conn.commit()
    # Optional: reclaim space
    cur.execute('VACUUM')
    conn.close()
    return True
