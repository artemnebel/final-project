# Program Name: app.py
# Author: Artem L. Nebel, Aurora Bardhoshi, Avaan S. Rayamajhi
# Date: 12/01/2025
#
# Description:
#   This program is a simple Fitness Tracker. It:
#       - Collects user information (age, weight, goal, timeline)
#       - Estimates a daily calorie goal
#       - Lets users log workouts (exercise, duration, calories burned)
#       - Lets users log meals (description, calories eaten)
#       - Shows daily summaries and overall trends
#
#   Data is stored using Python dictionaries and lists.
#   The program runs in a loop with a text-based menu so the user
#   can perform multiple actions in one session.

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from datetime import datetime, timedelta
import json
import os
import logging

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'aaa_fitness_tracker_secret_key_12345'
app.config['SESSION_COOKIE_SECURE'] = False  # Allow HTTP (development)
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.permanent_session_lifetime = timedelta(days=7)

# Initialize DB and keep using session for profile
import db
db.init_db()

# Import teammate modules (for reference - their code is incorporated into this Flask app)
# These modules contain the original command-line versions of the fitness tracker

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper functions
def calculate_calorie_goal(age, current_weight, goal_weight, weeks):
    """Calculate daily calorie goal based on user input"""
    days = weeks * 7
    pounds_change = goal_weight - current_weight
    total_calorie_change = pounds_change * 3500
    
    if days != 0:
        daily_calorie_change = total_calorie_change / days
    else:
        daily_calorie_change = 0
    
    estimated_maintenance = current_weight * 15
    suggested_daily_calories = estimated_maintenance + daily_calorie_change
    
    if suggested_daily_calories < 1200:
        suggested_daily_calories = 1200
    
    return {
        "age": age,
        "current_weight": current_weight,
        "goal_weight": goal_weight,
        "weeks": weeks,
        "days": days,
        "pounds_change": pounds_change,
        "total_calorie_change": total_calorie_change,
        "daily_calorie_change": daily_calorie_change,
        "estimated_maintenance": estimated_maintenance,
        "daily_calorie_goal": suggested_daily_calories
    }


@app.route('/')
def index():
    """Home page - serve the static HTML fitness tracker"""
    # Serve the index.html file which contains the full client-side app
    return send_from_directory('.', 'index.html')


@app.before_request
def make_session_permanent():
    """Make sessions permanent"""
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=7)


@app.route('/api/survey', methods=['POST'])
def submit_survey():
    """Handle user survey submission"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        age = int(data.get('age', 0))
        current_weight = float(data.get('current_weight', 0))
        goal_weight = float(data.get('goal_weight', 0))
        weeks = float(data.get('weeks', 0))
        
        if age <= 0 or current_weight <= 0 or weeks <= 0:
            return jsonify({"error": "Age, weight, and timeline must be positive"}), 400
        
        profile = calculate_calorie_goal(age, current_weight, goal_weight, weeks)
        
        # Save to session
        session['user_profile'] = profile
        session.permanent = True
        session.modified = True

        logger.info("Survey submitted successfully")

        return jsonify({"success": True, "profile": profile})
    except ValueError as e:
        logger.warning("ValueError in submit_survey: %s", str(e))
        return jsonify({"error": f"Invalid input values: {str(e)}"}), 400
    except Exception as e:
        logger.exception("Error in submit_survey")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


@app.route('/api/add-workout', methods=['POST'])
def add_workout():
    """Add a new workout"""
    if 'user_profile' not in session:
        return jsonify({"error": "User profile not found"}), 400
    
    data = request.json
    
    try:
        date = data.get('date')
        name = data.get('exercise_name')
        duration = float(data.get('duration'))
        calories = float(data.get('calories'))
        
        if not date or not name or duration <= 0 or calories <= 0:
            return jsonify({"error": "Invalid input"}), 400
        
        db.add_workout(date, name, duration, calories)
        return jsonify({"success": True, "message": "Workout added successfully"})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input values"}), 400


@app.route('/api/workouts/<date>')
def get_workouts(date):
    """Get all workouts for a specific date"""
    workouts, total_calories = db.get_workouts_for_date(date)
    return jsonify({"workouts": workouts, "total_calories": total_calories})


@app.route('/api/all-workouts')
def get_all_workouts():
    """Get all workouts grouped by date"""
    return jsonify(workouts_data)


@app.route('/api/add-meal', methods=['POST'])
def add_meal():
    """Add a new meal"""
    if 'user_profile' not in session:
        return jsonify({"error": "User profile not found"}), 400
    
    data = request.json
    
    try:
        date = data.get('date')
        description = data.get('description')
        calories = float(data.get('calories'))
        
        if not date or not description or calories <= 0:
            return jsonify({"error": "Invalid input"}), 400
        
        db.add_meal(date, description, calories)
        return jsonify({"success": True, "message": "Meal added successfully"})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid input values"}), 400


@app.route('/api/meals/<date>')
def get_meals(date):
    """Get all meals for a specific date"""
    meals, total_calories = db.get_meals_for_date(date)
    return jsonify({"meals": meals, "total_calories": total_calories})


@app.route('/api/daily-summary/<date>')
def get_daily_summary(date):
    """Get daily summary for a specific date"""
    if 'user_profile' not in session:
        return jsonify({"error": "User profile not found"}), 400
    workouts, calories_burned = db.get_workouts_for_date(date)
    meals, calories_eaten = db.get_meals_for_date(date)
    net_calories = calories_eaten - calories_burned
    daily_goal = session['user_profile']['daily_calorie_goal']
    
    return jsonify({
        "date": date,
        "workouts": workouts,
        "meals": meals,
        "calories_burned": calories_burned,
        "calories_eaten": calories_eaten,
        "net_calories": net_calories,
        "daily_goal": daily_goal,
        "remaining": daily_goal - net_calories
    })


@app.route('/api/reset-profile', methods=['POST'])
def reset_profile():
    """Reset user profile and start over"""
    # Clear session profile
    session.clear()
    # Also clear persisted user data so the dashboard shows empty state
    try:
        db.clear_all_data()
    except Exception as e:
        logger.warning("Warning: failed to clear DB during reset: %s", e)
    return jsonify({"success": True})


# Register tracking blueprint (adds /api/complete-day, /api/weight, /api/weights)
try:
    from tracking import tracking_bp
    app.register_blueprint(tracking_bp)
except Exception as e:
    logger.warning("Warning: failed to register tracking blueprint: %s", e)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
