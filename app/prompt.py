def get_trip_plan_prompt(start_location, destination, num_days, start_date, end_date, budget=None, weather_data=None):
    """
    Generate a comprehensive and detailed trip plan prompt for the AI.
    Includes budget constraint with support for multiple currencies and weather information.
    """
    # Default budget handling
    budget_text = ""
    if budget:
        symbol = budget.get("symbol", "$")  # Default to "$" if symbol not provided
        budget_amount = budget.get("amount", 0)
        budget_currency = budget.get("currency", "USD")

        # Handle unexpected types in budget_amount
        if isinstance(budget_amount, dict):
            budget_amount = budget_amount.get("value", 0)

        # Ensure budget_amount is a number
        budget_amount = float(budget_amount) if isinstance(budget_amount, (int, float, str)) else 0

        # Currency-specific formatting
        currency_format = {
            "USD": {"format": "${:,.2f}", "name": "US Dollars"},
            "EUR": {"format": "€{:,.2f}", "name": "Euros"},
            "GBP": {"format": "£{:,.2f}", "name": "British Pounds"},
            "JPY": {"format": "¥{:,.0f}", "name": "Japanese Yen"},  # No decimals for Yen
            "AUD": {"format": "A${:,.2f}", "name": "Australian Dollars"},
            "CAD": {"format": "C${:,.2f}", "name": "Canadian Dollars"},
            "INR": {"format": "₹{:,.2f}", "name": "Indian Rupees"},
            "CNY": {"format": "¥{:,.2f}", "name": "Chinese Yuan"}
        }

        # Get currency formatting or use default
        curr_format = currency_format.get(budget_currency, {"format": "${:,.2f}", "name": "USD"})
        formatted_amount = curr_format["format"].format(budget_amount)
        currency_name = curr_format["name"]

        # Generate budget constraint text with currency-specific guidance
        budget_text = f"""
        \nBUDGET CONSTRAINTS AND GUIDELINES:
        Total Budget: {formatted_amount} ({currency_name})

        Please ensure all recommendations and activities fit within this budget:
        - Provide cost breakdowns in {budget_currency}
        - Include budget-friendly alternatives where possible
        - Prioritize value-for-money options
        - Consider typical pricing in {destination} relative to this budget
        - Factor in common tourist price ranges for:
          * Accommodation
          * Local transportation
          * Meals and dining
          * Activities and attractions
          * Shopping and souvenirs
        
        Budget Distribution Guidelines:
        - Accommodation: ~30-40% of total budget
        - Transportation: ~20-25% of total budget
        - Food and Dining: ~20-25% of total budget
        - Activities and Entertainment: ~10-15% of total budget
        - Miscellaneous/Emergency: ~5-10% of total budget

        For each recommendation, please:
        1. Include specific costs in {budget_currency}
        2. Suggest money-saving tips when possible
        3. Highlight free or low-cost alternatives
        4. Note peak vs. off-peak pricing where relevant
        """

    return f"""Create a comprehensive and detailed {num_days}-day trip itinerary for traveling from {start_location} to {destination}, scheduled from {start_date} to {end_date}.

    1. INTRODUCTION: Begin with an engaging introduction about {destination}. Highlight its unique attractions, historical or cultural significance, and explain why it is an excellent travel choice. Include a brief overview of the experiences, cultural elements, and notable features travelers can expect during the trip.

    2. BEST ROUTE FOR THE TRIP**  
         Provide detailed recommendations for the most convenient and enjoyable travel options:  

         Recommended Route:  
               - Highlight the best mode of transportation (train, bus, car, or flight) based on travel time, cost, and convenience.  

         Transportation Details:  
               - Train: Include train names, departure/arrival times, notable stops, and famous food items at stations or onboard.  
               - Bus or Car: Mention schedules, routes, amenities, and scenic stops.  
               - Flights: Specify airlines, flight times, and proximity of airports to the destination.  

         Estimated Cost: Provide ticket or travel cost per person for each option.  

         Special Features: Note unique experiences like scenic views, onboard dining, or entertainment.  

         Alternative Options: Suggest backup routes or travel modes if the recommended route is unavailable.  

    3. ACCOMMODATION: Suggest places to stay for each night of the trip:
       - Include the name of the accommodation, its proximity to major attractions, and notable amenities.
       - Estimated Timing: Specify the exact arrival time at each accommodation (not just check-in or check-out times).
       - Estimated Cost: Provide the nightly cost range for the stay.
       Budget-Friendly Options

         Name and Location: Suggest affordable accommodations close to major attractions or well-connected to public transportation.
         Proximity: Highlight its distance to key destinations or landmarks.
         Amenities: Mention features such as free Wi-Fi, breakfast, shared kitchen facilities, or complimentary toiletries.
         Estimated Timing: Include the exact arrival time and any necessary check-in details.
         Estimated Cost: Provide a cost range that is economical for middle-class travelers.
         Mid-Range or Premium Options

         Name and Location: Suggest higher-end accommodations for those seeking enhanced comfort and amenities.
         Proximity: Note its strategic location, such as in the city center or near popular attractions.
         Amenities: Highlight notable features like pools, on-site dining, or private balconies.
         Estimated Timing: Specify arrival time and key check-in details.
         Estimated Cost: Provide a higher cost range for this category.

    4. Daily Itinerary: For each day of the trip, create a structured plan with a short, descriptive title (e.g., "Exploration and Adventure", "Relaxation and Sightseeing"). Include:
       - Morning Activities: Specify attractions or activities with detailed descriptions.
       - Afternoon Activities: Include sightseeing spots, entertainment, or leisure options.
       - Evening Activities: Add dining, entertainment, or relaxation plans.
       - For each activity:
         - Estimated Timing: Mention the start and end times for the activity.
         - Estimated Cost: Provide the approximate cost per person.

    5. FAMOUS FOOD ITEMS: Highlight the iconic and must-try food items in {destination}. Include:
       - Regional Specialties: List famous dishes unique to the region and provide a brief description of their significance or ingredients.
       - Where to Try: Recommend specific restaurants, food stalls, or markets where travelers can experience these delicacies.
       - Estimated Cost: Provide a cost range for these food items.
       - Food Culture Insights: Share interesting cultural or historical facts about the food in {destination}.

    6. Dining Recommendations: For each day, suggest restaurants for breakfast, lunch, and dinner:
       - Highlight specialty dishes or famous food items unique to each location in {destination}.
       - Include any famous food stalls, markets, or train station delicacies encountered during the journey.
       - Mention popular food streets or markets if applicable.
       - Estimated Timing: Include meal times.
       - Estimated Cost: Provide the cost range per person for each meal.

    7. Transportation Within Destination: Provide transportation tips for navigating {destination}, including:
       - Modes of transport (e.g., local trains, taxis, bikes, buses).
       - Estimated Timing: Time required to travel between locations.
       - Estimated Cost: Cost of transportation per person.

    8. Final Summary:
       - Include a bullet-point summary of the total estimated budget for the trip:
         - Accommodation: Total cost for the stay.
         - Meals: Total food expenses.
         - Transportation: Total cost of travel, including intercity and local transportation.
         - Activities: Total cost for entry fees and other expenses.
         - Total Cost Per Person: Add all the costs.


    Ensure the itinerary is formatted with clear sections and subheadings for each day, and use bullet points for each activity's timing and cost. Present the information in a friendly, professional tone that is engaging and informative.{budget_text}"""