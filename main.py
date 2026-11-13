# import os
# import requests
# import gradio as gr
# from dotenv import load_dotenv
# from langchain.chat_models import init_chat_model
# from langchain.agents import create_agent




# load_dotenv()


# def get_weather(city:str):
#     """Fetches the current weather for a given city using the OpenWeatherMap API."""
#     api_key=os.getenv("WEATHER_API_KEY")
#     base_url="http://api.openweathermap.org/data/2.5/weather"
#     params={
#         "q":city,
#         "appid":api_key,
#         "units":"metric",
#     }
#     response=requests.get(base_url,params=params)
#     data=response.json()
#     temp_celsius=data["main"]["temp"]
#     temp_fahrenheit=(temp_celsius*9/5)+32
#     return data,{"temp_fahrenheit":temp_fahrenheit}



# def get_location():
#     """Fetches the current location of the user based on their IP address."""
#     response=requests.get("https://ipapi.co/json/",headers={"User-agent":"your-bot 0.1"})
#     data=response.json()
#     city=data['city']
#     country=data['country_name']
#     return f"{city}, {country}"


# #initilize model
# llm=init_chat_model(
#     model="gemma4:31b-cloud",
#     model_provider="ollama",
# )

# system_prompt="""
# You are a weather agent that can provide current weather information for any city in the world.

# """

# #create agent
# agent=create_agent(
#     model=llm,
#     tools=[get_weather,get_location],
#     system_prompt=system_prompt
# )


# # Function called when the user sends a message
# def chat(message, history):
#     response = agent.invoke({
#         "messages": [{"role": "user", "content": message}]
#     })

#     return response["messages"][-1].content

# # Create the chat interface
# demo = gr.ChatInterface(
#     fn=chat,
#     title="My Weather AI Chatbot",
#     description="Ask about the Weather"
# )

# # Start the application
# demo.launch(debug=True)












































import os
import requests
import gradio as gr

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent


# STEP 1: Load environment variables
load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY not found in .env")


# STEP 2: Weather tool
def get_weather(city: str) -> dict:
    """Get current weather information for a city."""

    base_url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(
            base_url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if "main" not in data:
            return {"error": "Weather information unavailable"}

        temp_celsius = data["main"]["temp"]
        temp_fahrenheit = (temp_celsius * 9 / 5) + 32

        return {
            "city": data["name"],
            "temperature_celsius": temp_celsius,
            "temperature_fahrenheit": round(temp_fahrenheit, 2),
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "wind_speed": data["wind"]["speed"]
        }

    except requests.RequestException as error:
        return {"error": f"Weather service error: {str(error)}"}


# STEP 3: Location tool
def get_location() -> dict:
    """Get approximate location based on the user's IP address."""

    try:
        response = requests.get(
            "https://ipapi.co/json/",
            headers={"User-Agent": "WeatherAssistant/1.0"},
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        if data.get("error"):
            return {"error": "Unable to determine location"}

        return {
            "city": data.get("city"),
            "country": data.get("country_name"),
            "location_type": "Approximate IP-based location"
        }

    except requests.RequestException:
        return {"error": "Location service is unavailable"}


# STEP 4: Initialize LLM
llm = init_chat_model(
    model="gemma4:31b-cloud",
    model_provider="ollama"
)


# STEP 5: System prompt
system_prompt = """
You are a helpful AI weather assistant.

You have access to two tools:
1. get_weather: Get current weather for a city.
2. get_location: Get the user's approximate IP-based location.

Rules:
- Use get_weather when users ask about a city's weather.
- Use get_location when users ask about their current location
  or the weather near them.
- Explain weather information in simple English.
- Use the actual tool results. Never invent weather data.
- If a tool returns an error, explain it clearly.
- Do not claim to know future rain probability from current
  weather data alone.
- Clearly identify approximate IP-based location.
"""


# STEP 6: Create AI agent
agent = create_agent(
    model=llm,
    tools=[get_weather, get_location],
    system_prompt=system_prompt
)


# STEP 7: Chat function
def chat(message, history):

    messages = []

    # Include previous conversation
    for item in history:

        role = item.get("role")
        content = item.get("content")

        if role in ["user", "assistant"] and isinstance(content, str):

            messages.append({
                "role": role,
                "content": content
            })

    # Add current question
    messages.append({
        "role": "user",
        "content": message
    })

    # Run AI agent
    response = agent.invoke({
        "messages": messages
    })

    return response["messages"][-1].content


# STEP 8: Gradio interface
demo = gr.ChatInterface(
    fn=chat,
    title="My Weather AI Agent",
    description="Ask about current weather in any city."
)


# STEP 9: Launch application
demo.launch(debug=True)




