import streamlit as st
import groq
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pdf_generator import generate_trip_pdf
from prompt import get_trip_plan_prompt
import requests

headers ={ 
   "authorization": st.secrets["GROQ_API_KEY"]
}

# Load environment variables
load_dotenv()

# Initialize Groq client with API key from .env
client = groq.Groq(
    api_key=os.getenv('GROQ_API_KEY')
)


def calculate_min_budget(start_location, destination, num_days):
    """
    Calculate minimum budget based on location and duration
    Returns minimum budget in INR
    """
    # Base daily costs (in INR)
    base_costs = {
        "domestic": {
            "budget": 2000,    # Basic accommodation, local food, public transport
            "mid": 5000,       # Better accommodation, mix of restaurants
            "luxury": 10000    # High-end hotels, fine dining
        },
        "international": {
            "nearby": {
                "budget": 5000,    # Nepal, Bangladesh, Sri Lanka, etc.
                "mid": 10000,
                "luxury": 20000
            },
            "medium": {
                "budget": 8000,    # Thailand, Malaysia, UAE, etc.
                "mid": 15000,
                "luxury": 30000
            },
            "far": {
                "budget": 12000,   # Europe, US, Australia, etc.
                "mid": 25000,
                "luxury": 50000
            }
        }
    }
    
    # Determine if international trip
    is_international = False
    distance_category = "domestic"
    
    # Common international destinations from India
    nearby_countries = ["nepal", "bangladesh", "sri lanka", "bhutan", "myanmar"]
    medium_distance = ["thailand", "malaysia", "singapore", "uae", "dubai", "vietnam", "cambodia", "indonesia"]
    far_countries = ["usa", "uk", "france", "germany", "italy", "spain", "australia", "japan", "canada"]
    
    # Clean and lower case the destination for comparison
    dest_lower = destination.lower()
    
    # Check if international and categorize distance
    if any(country in dest_lower for country in nearby_countries):
        is_international = True
        distance_category = "nearby"
    elif any(country in dest_lower for country in medium_distance):
        is_international = True
        distance_category = "medium"
    elif any(country in dest_lower for country in far_countries):
        is_international = True
        distance_category = "far"
    
    # Calculate base daily cost
    if is_international:
        daily_min = base_costs["international"][distance_category]["budget"]
    else:
        daily_min = base_costs["domestic"]["budget"]
    
    # Calculate total minimum budget
    min_budget = daily_min * num_days
    
    # Add transportation cost estimate
    if is_international:
        if distance_category == "nearby":
            min_budget += 15000  # Basic international flight/transport cost
        elif distance_category == "medium":
            min_budget += 30000
        else:  # far
            min_budget += 60000
    else:
        min_budget += 5000  # Basic domestic travel cost
    
    return min_budget

def get_trip_plan(start_location, destination, num_days, start_date, end_date, budget=None):
    """Generate a trip plan using Llama model through Groq API"""
    
    prompt = get_trip_plan_prompt(start_location, destination, num_days, start_date, end_date, budget)

    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=4000
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating trip plan: {str(e)} or No network!"

# Set page config
st.set_page_config(
    page_title="TripAI",
    page_icon="✈",
    layout="wide"
)

# Simple left navigation
with st.sidebar:
    st.title("🌎 TripAI")
    st.markdown("---")
    st.markdown("### Menu")
    st.markdown("🏠 Home")
    st.markdown("✈ Plan Trip")
    st.markdown("📝 My Trips")

# Main content
st.title("Trip Planner & Travel guide")
st.write("Plan your perfect trip with AI assistance!")
st.write("Developed by Rebooterz!")

# First row - Location inputs
loc_col1, loc_col2 = st.columns(2)

with loc_col1:
    start_location = st.text_input("Starting Location:", 
                                 placeholder="e.g., Chennai, India")

with loc_col2:
    destination = st.text_input("Destination:", 
                              placeholder="e.g., Paris, France")

# Second row - Date inputs
date_col1, date_col2 = st.columns(2)

with date_col1:
    min_date = datetime.now()
    max_date = datetime.now() + timedelta(days=365)
    start_date = st.date_input("Start Date",
                              min_value=min_date,
                              max_value=max_date,
                              value=min_date)

with date_col2:
    end_date = st.date_input("End Date",
                            min_value=start_date,
                            max_value=max_date,
                            value=start_date + timedelta(days=3))

# Calculate number of days
num_days = None
if start_date and end_date:
    num_days = (end_date - start_date).days + 1
    st.info(f"Trip Duration: {num_days} days")

# Budget section (always shown with minimum validation)
budget_col1, budget_col2 = st.columns(2)

with budget_col1:
    currency = st.selectbox(
        "Select Currency",
        [
            "INR - Indian Rupee",  # Made INR the default
            "USD - US Dollar",
            "EUR - Euro",
            "GBP - British Pound",
            "JPY - Japanese Yen",
            "AUD - Australian Dollar",
            "CAD - Canadian Dollar",
            "CNY - Chinese Yuan",
        ]
    )
    currency_code = currency.split(" - ")[0]
    
    # Currency symbols dictionary
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "AUD": "A$",
        "CAD": "C$",
        "INR": "₹",
        "CNY": "¥"
    }

with budget_col2:
    # Calculate minimum budget if we have all required information
    min_budget = 1000  # Absolute minimum in INR
    if start_location and destination and num_days:
        min_budget = calculate_min_budget(start_location, destination, num_days)
    
    # Convert minimum budget to selected currency
    # Note: Using simple conversion rates for demonstration
    conversion_rates = {
        "USD": 0.012,  # 1 INR = 0.012 USD
        "EUR": 0.011,
        "GBP": 0.0095,
        "JPY": 1.35,
        "AUD": 0.018,
        "CAD": 0.016,
        "INR": 1.0,
        "CNY": 0.086
    }
    
    min_budget_currency = min_budget * conversion_rates[currency_code]
    
    budget_amount = st.number_input(
        "Enter your budget(for one person)",
        min_value=float(min_budget_currency),
        value=float(min_budget_currency * 1.2),  # Set default to 20% above minimum
        step=min_budget_currency/20,  # Set step size to 5% of minimum budget
        help=f"Minimum recommended budget for this trip: {currency_symbols[currency_code]}{min_budget_currency:,.2f}"
    )

budget = {
    "amount": budget_amount,
    "currency": currency_code,
    "symbol": currency_symbols.get(currency_code, "$")
}

# Generate button
if st.button("Generate Trip Plan", type="primary"):
    if not start_location or not destination:
        st.error("Please enter both starting location and destination")
    elif start_date > end_date:
        st.error("End date must be after start date")
    else:
        with st.spinner("Generating your perfect trip plan..."):
            plan_placeholder = st.empty()
            trip_plan = get_trip_plan(start_location, destination, num_days, start_date, end_date, budget)
            plan_placeholder.markdown(trip_plan)
            
            # Generate PDF
            pdf_path = generate_trip_pdf(
                trip_plan, 
                start_location, 
                destination, 
                start_date, 
                end_date
            )
            
            # Store PDF in session state
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Download Trip Plan PDF",
                    data=pdf_file,
                    file_name=f"trip_plan_{start_location}to{destination}_{start_date}.pdf",
                    mime="application/pdf"
                )
            # Clean up PDF file
            os.remove(pdf_path)

# Footer
st.markdown("---")
st.markdown("""
### How to use:
1. Enter your starting location and destination
2. Select your travel dates (the number of days will be calculated automatically)
3. Enter your budget (the minimum recommended budget will be calculated based on your trip details)
4. Click 'Generate Trip Plan' to get your customized itinerary
5. Download your plan as a PDF

Note: The minimum budget is calculated based on:
- Trip duration
- Destination type (domestic/international)
- Basic travel costs
- Essential daily expenses
""")
