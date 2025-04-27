from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.schema.messages import SystemMessage
from dotenv import load_dotenv
import os
import json
import openai
from dotenv import load_dotenv
from utils import get_flight_options, get_hotel_options

# Load environment variables
load_dotenv()

# Initialize OpenAI chat model
chat = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-3.5-turbo",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Initialize memory with conversation buffer
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

def gpt_call_with_functions(prompt):
    functions = [
        {
            "name": "get_flight_options",
            "description": "Fetch flight options for a destination",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "dates": {"type": "string"}
                },
                "required": ["destination", "dates"]
            }
        },
        {
            "name": "get_hotel_options",
            "description": "Fetch hotel options for a destination",
            "parameters": {
                "type": "object",
                "properties": {
                    "destination": {"type": "string"},
                    "dates": {"type": "string"},
                    "budget_per_night": {"type": "number"}
                },
                "required": ["destination", "dates", "budget_per_night"]
            }
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4-0613",
        messages=[
            {"role": "user", "content": prompt}
        ],
        functions=functions,
        function_call="auto"  # let GPT-4 decide
    )

    return response['choices'][0]['message']

# Usage
# reply = gpt_call_with_functions("Find flights to Paris for 10th Oct")
# print(reply)

# Define tools for the agent
tools = [
    Tool(
        name="search_travel_options",
        func=lambda x: generate_travel_options(x),
        description="Search for travel options based on user preferences"
    ),
    Tool(
        name="get_travel_package",
        func=lambda x: generate_travel_package(x),
        description="Create a custom travel package"
    )
]

# Helper functions for the tools
def generate_travel_options(input_data):
    """Generate travel options based on user preferences"""
    try:
        # Parse input data
        preferences = json.loads(input_data)
        # Validate input data
        if not isinstance(preferences, dict):
            raise ValueError("Invalid input format")
        # Generate sample options (in real implementation, this would query APIs)
        options = {
            "flights": {
                "options": [
                    {"airline": "Air France", "price": "$800", "duration": "10h"},
                    {"airline": "Lufthansa", "price": "$850", "duration": "11h"}
                ]
            },
            "hotels": {
                "options": [
                    {"name": "Disneyland Hotel", "price": "$120/night", "rating": "4.5"},
                    {"name": "Hotel Louvre Marsollier", "price": "$150/night", "rating": "4.7"}
                ]
            },
            "activities": {
                "options": [
                    {"name": "Disneyland Paris", "price": "$100/person", "duration": "1 day"},
                    {"name": "Louvre Museum", "price": "$30/person", "duration": "3h"},
                    {"name": "Seine River Cruise", "price": "$40/person", "duration": "2h"}
                ]
            }
        }
        
        return json.dumps(options)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON input")
    except Exception as e:
        return f"Error generating options: {str(e)}"

def generate_travel_package(input_data):
    """Generate a complete travel package based on preferences"""
    try:
        # Parse input data
        preferences = json.loads(input_data)
        
        # Generate package based on preferences
        package = {
            "destination": preferences.get("destination", "Paris"),
            "dates": preferences.get("dates", "10th Oct to 20th Oct"),
            "budget": preferences.get("budget", "$2000"),
            "type": preferences.get("type", "Family vacation"),
            "activities": preferences.get("activities", ["Disneyland", "Museums"]),
            
            "package_details": {
                "flights": {
                    "airline": "Air France",
                    "price": "$800",
                    "duration": "10h"
                },
                "hotel": {
                    "name": "Disneyland Hotel",
                    "price": "$120/night",
                    "total": "$1200"
                },
                "activities": [
                    {"name": "Disneyland full-day pass", "price": "$100/person"},
                    {"name": "Louvre Museum skip-the-line tickets", "price": "$30/person"},
                    {"name": "Seine River family boat cruise", "price": "$40/person"}
                ],
                "total_estimated_cost": "$1800",
                "travel_tips": "Pack for fall weather! Bring comfortable shoes for walking and consider renting strollers for young children."
            }
        }
        
        return json.dumps(package)
    except Exception as e:
        return f"Error generating package: {str(e)}"

# Initialize the agent with system message
system_message = SystemMessage(
    content="""
    You are TravelBuddy AI, a travel planning assistant.
    Your goal is to:
    1. Welcome the user and explain your capabilities
    2. Ask questions about travel preferences in this order:
       a. Destination
       b. Travel dates
       c. Budget range
       d. Type of travel (Adventure, Relaxation, Family, Honeymoon)
       e. Special activities or preferences
    3. After collecting 5 pieces of information, automatically generate a travel package
    4. Present the package in a clear, structured format
    5. Allow users to modify preferences if needed
    
    Always maintain a friendly and helpful tone.
    Keep track of user preferences in memory.
    Generate package suggestions based on user's budget and preferences.
    """
)
def optimize_activities(budget_remaining):
    activities = [
        {"activity": "Disneyland Full Day Pass", "cost": 120},
        {"activity": "Louvre Museum Guided Tour", "cost": 60},
        {"activity": "Seine River Cruise", "cost": 45},
        {"activity": "Paris City Bike Tour", "cost": 50},
        {"activity": "Wine Tasting Experience", "cost": 80},
        {"activity": "Versailles Day Trip", "cost": 100}
    ]

    selected = []
    total_spent = 0

    for activity in sorted(activities, key=lambda x: x['cost']):
        if total_spent + activity["cost"] <= budget_remaining:
            selected.append(activity)
            total_spent += activity["cost"]

    return selected, total_spent

# Initialize the agent
agent = initialize_agent(
    tools,
    chat,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    system_message=system_message,
    verbose=True
)

# Export the agent for use in other modules
if __name__ == "__main__":
    print("TravelBuddy AI agent initialized successfully!")