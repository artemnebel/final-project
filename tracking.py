from flask import Blueprint, request, jsonify, session
from datetime import datetime
import db

tracking_bp = Blueprint('tracking', __name__)


@tracking_bp.route('/api/complete-day', methods=['POST'])
def complete_day():
    data = request.get_json() or {}
    date = data.get('date')
    if not date:
        return jsonify({"error": "date is required"}), 400

    # Use db helpers to fetch meals and workouts for the date
    meals, calories_eaten = db.get_meals_for_date(date)
    workouts, calories_burned = db.get_workouts_for_date(date)

    # Get daily goal from session if available
    daily_goal = 0
    if 'user_profile' in session:
        daily_goal = session['user_profile'].get('daily_calorie_goal', 0)

    net_calories = calories_eaten - calories_burned

    percent_reached = 0
    if daily_goal > 0:
        percent_reached = int(round(max(0, min(100, (net_calories / daily_goal) * 100))))

    # Persist completed day record
    try:
        db.add_completed_day(date, calories_eaten, calories_burned, net_calories, daily_goal, percent_reached)
    except Exception:
        # Non-fatal: still return the computation
        pass

    result = {
        "date": date,
        "calories_eaten": calories_eaten,
        "calories_burned": calories_burned,
        "net_calories": net_calories,
        "daily_goal": daily_goal,
        "percent_reached": percent_reached
    }

    return jsonify(result)


@tracking_bp.route('/api/weight', methods=['POST'])
def add_weight():
    data = request.get_json() or {}
    date = data.get('date')
    weight = data.get('weight')

    if not date or weight is None:
        return jsonify({"error": "date and weight are required"}), 400

    try:
        key = db.add_weight(date, float(weight))
    except Exception as e:
        return jsonify({"error": f"invalid data: {e}"}), 400

    return jsonify({"success": True, "week": key, "weight": float(weight)})


@tracking_bp.route('/api/weights')
def get_weights():
    try:
        items = db.get_weights()
    except Exception:
        items = []
    return jsonify({"weights": items})
