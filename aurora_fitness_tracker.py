
# Program Name: fitness_tracker.py
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



# Will store user info after the survey
user_profile = None

# Workouts and meals will be stored by date (string like "2025-12-01")
# Example:
#   workouts_data["2025-12-01"] = [
#       {"name": "Squats", "duration": 30, "calories": 150},
#       {"name": "Running", "duration": 20, "calories": 200}
#   ]
workouts_data = {}

# Example:
#   meals_data["2025-12-01"] = [
#       {"description": "Breakfast - oatmeal", "calories": 350},
#       {"description": "Lunch - salad", "calories": 500}
#   ]
meals_data = {}


# -----------------------------
#   HELPER FUNCTIONS
# -----------------------------

def get_non_empty_string(prompt):
    """
    Ask user for a non-empty string.
    """
    while True:
        value = input(prompt).strip()
        if value != "":
            return value
        print("Input cannot be empty. Please try again.")


def get_positive_float(prompt):
    """
    Ask user for a positive floating-point number.
    """
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            else:
                print("Value must be positive. Try again.")
        except ValueError:
            print("Invalid number. Try again.")


def get_positive_int(prompt):
    """
    Ask user for a positive integer.
    """
    while True:
        try:
            value = int(input(prompt))
            if value > 0:
                return value
            else:
                print("Value must be a positive integer. Try again.")
        except ValueError:
            print("Invalid integer. Try again.")




# Function: user_survey
# Parameters: none
# Returns: a dictionary with the user’s info and calorie goal
#
# Description:
#   This function asks the user for their age, current weight,
#   goal weight, and timeline. It then calculates how many pounds
#   they want to change and gives a simple daily calorie goal.


def user_survey():
    print("\n    Fitness Tracker: User Survey    ")

    age = get_positive_int("Enter your age (years): ")
    current_weight = get_positive_float("Enter your current weight (lbs): ")
    goal_weight = get_positive_float("Enter your goal weight (lbs): ")
    weeks = get_positive_float("Enter your timeline (in weeks): ")

    days = weeks * 7

    # Pounds to change
    pounds_change = goal_weight - current_weight  # positive = gain, negative = lose

    # 1 pound of body weight is approximately 3500 calories
    total_calorie_change = pounds_change * 3500

    # Daily calorie change needed
    if days != 0:
        daily_calorie_change = total_calorie_change / days
    else:
        daily_calorie_change = 0

    # Simple "maintenance" estimate: ~15 calories per pound of body weight
    # This is a very rough estimate, just for the project.
    estimated_maintenance = current_weight * 15

    # Suggested daily calories = maintenance + change
    suggested_daily_calories = estimated_maintenance + daily_calorie_change

    # Make sure daily calories are not unrealistically low
    if suggested_daily_calories < 1200:
        suggested_daily_calories = 1200

    profile = {
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

    print("\n--- Survey Summary ---")
    print(f"Age: {age} years")
    print(f"Current weight: {current_weight:.1f} lbs")
    print(f"Goal weight: {goal_weight:.1f} lbs")
    if pounds_change < 0:
        print(f"You want to lose about {abs(pounds_change):.1f} lbs.")
    elif pounds_change > 0:
        print(f"You want to gain about {pounds_change:.1f} lbs.")
    else:
        print("Your goal weight is the same as your current weight.")

    print(f"Timeline: {weeks:.1f} week(s) ({days:.0f} days)")
    print(f"Total calorie change needed: {total_calorie_change:.0f} calories")
    print(f"Estimated maintenance: {estimated_maintenance:.0f} cal/day")
    print(f"Suggested daily calorie goal: {suggested_daily_calories:.0f} cal/day")

    print("\nYour profile has been saved and will be used for summaries.\n")

    return profile


# -----------------------------
#   WORKOUT LOGGING
# -----------------------------

# Function: add_workout
# Parameters: none
# Returns: nothing
#
# Description:
#   Lets the user add a workout by entering:
#       - date
#       - exercise name
#       - duration
#       - calories burned
#   Saves the workout to the workout log.

def add_workout():
    print("\n    Add Workout    ")
    date = get_non_empty_string("Enter date (e.g., 2025-12-01): ")
    name = get_non_empty_string("Exercise name: ")
    duration = get_positive_float("Duration (minutes): ")
    calories = get_positive_float("Calories burned: ")

    workout_entry = {
        "name": name,
        "duration": duration,
        "calories": calories
    }

    # Add to correct date list
    if date not in workouts_data:
        workouts_data[date] = []
    workouts_data[date].append(workout_entry)

    print("\nWorkout added successfully.\n")


def view_workouts_for_date(date):

    #Print all workouts for a given date and return total calories burned.

    if date not in workouts_data or len(workouts_data[date]) == 0:
        print("No workouts logged for this date.")
        return 0.0

    print("\n--- Workouts ---")
    total_burned = 0.0
    for i, workout in enumerate(workouts_data[date], start=1):
        print(f"{i}. {workout['name']} - {workout['duration']} min, "
              f"{workout['calories']} cal")
        total_burned += workout["calories"]

    print(f"Total calories burned: {total_burned:.1f}")
    return total_burned


# Main menu
if __name__ == "__main__":
    print("Welcome to Aurora Fitness Tracker!")
    
    # Start with user survey
    user_profile = user_survey()
    
    # Main loop
    while True:
        print("\n--- Main Menu ---")
        print("1. Add Workout")
        print("2. View Workouts")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            add_workout()
        elif choice == "2":
            date = input("Enter date to view workouts (e.g., 2025-12-01): ").strip()
            view_workouts_for_date(date)
        elif choice == "3":
            print("Thank you for using Aurora Fitness Tracker!")
            break
        else:
            print("Invalid choice. Please try again.")
