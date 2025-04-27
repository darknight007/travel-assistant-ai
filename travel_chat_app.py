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