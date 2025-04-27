# travel_chat_app.py
import streamlit as st
from app.utils import agent
import time

# Set page configuration
st.set_page_config(
    page_title="TravelBuddy AI",
    page_icon="✈️",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .stTextInput input {
            border: 2px solid #4CAF50;
            border-radius: 8px;
            padding: 12px;
            font-size: 16px;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 16px;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
    </style>
""", unsafe_allow_html=True)

# Main content
st.title("✈️ TravelBuddy AI - Your Personal Travel Consultant")
st.write("Welcome to your personalized travel planning experience!")

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'destination' not in st.session_state:
    st.session_state.destination = ""
if 'dates' not in st.session_state:
    st.session_state.dates = ""
if 'budget' not in st.session_state:
    st.session_state.budget = ""
if 'preferences' not in st.session_state:
    st.session_state.preferences = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Step-by-step consultation flow
if st.session_state.step == 0:
    st.header("Step 1: Where would you like to go?")
    st.write("Please share your dream destination with us!")
    destination = st.text_input("Destination", placeholder="e.g., Paris, France")
    if st.button("Next") and destination:
        st.session_state.destination = destination
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 1:
    st.header("Step 2: When are you planning to travel?")
    st.write(f"Great choice! {st.session_state.destination} is a fantastic destination!")
    st.write("When would you like to visit?")
    dates = st.text_input("Dates", placeholder="e.g., May 15 - May 25, 2025")
    if st.button("Next") and dates:
        st.session_state.dates = dates
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    st.header("Step 3: What's your budget?")
    st.write("Let's make sure we find options that fit your budget!")
    budget = st.text_input("Budget", placeholder="e.g., $2000 per person")
    if st.button("Next") and budget:
        st.session_state.budget = budget
        st.session_state.step = 3
        st.rerun()

elif st.session_state.step == 3:
    st.header("Step 4: Your preferences")
    st.write("Help us tailor your trip to your preferences!")
    preferences = st.text_area("Preferences", 
        placeholder="e.g., Adventure activities, luxury accommodations, cultural experiences")
    if st.button("Next") and preferences:
        st.session_state.preferences = preferences
        st.session_state.step = 4
        st.rerun()

elif st.session_state.step == 4:
    st.header("Let's create your perfect trip!")
    st.write("I'll analyze your preferences and create a tailored travel package.")
    
    # Prepare the prompt with all collected information
    prompt = f"""
    User wants to travel to {st.session_state.destination} from {st.session_state.dates}.
    Budget: {st.session_state.budget}
    Preferences: {st.session_state.preferences}
    
    Please create a comprehensive travel package including:
    1. Flight options
    2. Accommodation suggestions
    3. Activity recommendations
    4. Budget breakdown
    
    Present the information in a clear, structured format.
    """
    
    # Get and display assistant response
    with st.spinner("Creating your perfect travel package..."):
        response = agent.invoke(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Display the chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Add a button to start over
    if st.button("Start Over"):
        st.session_state.step = 0
        st.session_state.destination = ""
        st.session_state.dates = ""
        st.session_state.budget = ""
        st.session_state.preferences = ""
        st.session_state.messages = []
        st.rerun()

# Add a footer
st.markdown("""
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f8f9fa;
            padding: 10px;
            text-align: center;
            font-size: 14px;
        }
    </style>
    <div class="footer">
        Created with ❤️ by TravelBuddy AI | All travel recommendations are subject to availability
    </div>
""", unsafe_allow_html=True)
st.sidebar.title("About")
st.sidebar.info(
    """
    TravelBuddy AI helps you create your personalized travel packages using AI!
    Built with ❤️ using LangChain and GPT-4.
    """
)
st.sidebar.header("🛫 Trip Preferences")

destination = st.sidebar.text_input("Destination")
start_date = st.sidebar.date_input("Start Date")
end_date = st.sidebar.date_input("End Date")
budget = st.sidebar.slider("Total Budget ($)", 500, 10000, 2000)
travel_type = st.sidebar.selectbox(
    "Travel Type",
    ("Adventure", "Relaxation", "Family Vacation", "Honeymoon", "Backpacking")
)

submit_button = st.sidebar.button("Plan My Trip!")
if submit_button:
    # 1. Show Chatbot Interaction (Optional)
    st.subheader("🧠 AI Conversation")

    with st.chat_message("user"):
        st.write(f"I'm planning a {travel_type.lower()} to {destination} from {start_date} to {end_date} with a ${budget} budget.")

    with st.chat_message("assistant"):
        st.write("Awesome! Let me craft a dream package for you... ✈️🏨🎉")

    # 2. Fetch Flights, Hotels (via function calling or dummy data)
    flights = get_flight_options(destination, f"{start_date} to {end_date}")
    hotels = get_hotel_options(destination, f"{start_date} to {end_date}", budget_per_night=(budget/5)/len(flights))

    st.subheader("✈️ Flight Options")
    st.table(flights)

    st.subheader("🏨 Hotel Options")
    st.table(hotels)

    # 3. Budget Optimization for Activities
    st.subheader("🎉 Optimized Activities under Your Budget")

    total_flight_hotel_cost = flights[0]['price'] + hotels[0]['price_per_night'] * 5  # 5 nights assumption
    remaining_budget = budget - total_flight_hotel_cost

    if remaining_budget > 0:
        activities, spent = optimize_activities(remaining_budget)
        st.success(f"Activities selected within your remaining budget (${remaining_budget:.2f}):")
        st.table(activities)
    else:
        st.warning("Your budget is fully utilized for travel and stay. No additional activities suggested.")
