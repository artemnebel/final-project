# -----------------------------
#   MEAL LOGGING
# -----------------------------

# Function: add_meal
# Parameters: none
# Returns: nothing
#
# Description:
#   Lets the user add a meal by entering:
#       - date
#       - meal description
#       - calories eaten
#   Saves the meal entry into meals_data.


def add_meal():
    print("\n    Add Meal    ")
    date = get_non_empty_string("Enter date (e.g., 2025-12-01): ")
    description = get_non_empty_string("Meal description: ")
    calories = get_positive_float("Calories eaten: ")

    meal_entry = {
        "description": description,
        "calories": calories
    }

    # Add to correct date list
    if date not in meals_data:
        meals_data[date] = []
    meals_data[date].append(meal_entry)

    print("\nMeal added successfully.\n")



def view_meals_for_date(date):
    """
    Print all meals for a given date and return
    the total calories eaten.
    """

    if date not in meals_data or len(meals_data[date]) == 0:
        print("No meals logged for this date.")
        return 0.0

    print("\n--- Meals ---")
    total_eaten = 0.0

    for i, meal in enumerate(meals_data[date], start=1):
        print(f"{i}. {meal['description']} - {meal['calories']} cal")
        total_eaten += meal["calories"]

    print(f"Total calories eaten: {total_eaten:.1f}")
    return total_eaten
