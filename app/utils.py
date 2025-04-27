# app/utils.py
from typing import Dict, List, Optional
import json
import time
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.schema.messages import SystemMessage
from dotenv import load_dotenv
import os
from openai import OpenAIError
import random

# Load environment variables
load_dotenv()

def call_with_retry(agent, prompt, max_retries=3, retry_delay=5):
    """Wrapper to handle rate limiting and retries"""
    for attempt in range(max_retries):
        try:
            response = agent.invoke(prompt)
            return response
        except OpenAIError as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        except Exception as e:
            raise

# Initialize OpenAI chat model with function calling
chat = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    request_timeout=30  # Add timeout
)

# Define travel data fetching functions
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: int = 1
) -> Dict:
    """Simulates flight search API call"""
    return {
        "flights": [
            {
                "airline": "Air France",
                "price": "$800",
                "duration": "10h",
                "departure_time": "09:00",
                "arrival_time": "19:00"
            },
            {
                "airline": "British Airways",
                "price": "$850",
                "duration": "11h",
                "departure_time": "11:30",
                "arrival_time": "22:30"
            }
        ]
    }

def search_hotels(
    destination: str,
    check_in: str,
    check_out: str,
    room_type: str = "standard",
    guests: int = 2
) -> Dict:
    """Simulates hotel search API call"""
    return {
        "hotels": [
            {
                "name": "Luxury Hotel",
                "rating": 5,
                "price_per_night": "$200",
                "amenities": ["Pool", "Spa", "Free WiFi"]
            },
            {
                "name": "Budget Hotel",
                "rating": 4,
                "price_per_night": "$120",
                "amenities": ["Free WiFi", "Breakfast"]
            }
        ]
    }

def search_activities(
    destination: str,
    date: str,
    category: str = "all",
    duration: Optional[str] = None
) -> Dict:
    """Simulates activity search API call"""
    return {
        "activities": [
            {
                "name": "City Tour",
                "price": "$50",
                "duration": "3h",
                "category": "sightseeing"
            },
            {
                "name": "Cooking Class",
                "price": "$75",
                "duration": "2h",
                "category": "cultural"
            }
        ]
    }

# Define tools for the agent
tools = [
    Tool(
        name="search_flights",
        func=search_flights,
        description="Search for flights based on origin, destination, and dates"
    ),
    Tool(
        name="search_hotels",
        func=search_hotels,
        description="Search for hotels in a specific location"
    ),
    Tool(
        name="search_activities",
        func=search_activities,
        description="Search for activities and tours in a destination"
    )
]

# System message for the agent
system_message = SystemMessage(
    content="""
    You are TravelBuddy AI, a travel planning assistant.
    Your goal is to help users plan their trips by:
    1. Understanding their travel preferences
    2. Using the available tools to find relevant options
    3. Creating comprehensive travel packages
    4. Presenting information in a clear, structured format
    
    Always maintain a friendly and helpful tone.
    Use the available tools to fetch real-time data.
    Generate package suggestions based on user's budget and preferences.
    """
)
def get_flight_options(destination, dates):
    # Simulated dummy flight options
    return [
        {"airline": "Air France", "price": random.randint(400, 800)},
        {"airline": "Emirates", "price": random.randint(450, 850)},
        {"airline": "Lufthansa", "price": random.randint(420, 790)}
    ]

def get_hotel_options(destination, dates, budget_per_night):
    # Simulated dummy hotels
    return [
        {"hotel_name": "Hotel Lux", "price_per_night": random.randint(100, 200)},
        {"hotel_name": "Comfort Suites", "price_per_night": random.randint(80, 150)},
        {"hotel_name": "City Inn", "price_per_night": random.randint(90, 170)}
    ]
# Initialize the agent with system message
agent = initialize_agent(
    tools,
    chat,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    handle_errors=True  # Enable error handling
)