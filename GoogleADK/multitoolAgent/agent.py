from google.adk.agents import LlmAgent
from google.adk.tools import google_search,FunctionTool, agent_tool


import requests, json
# custom tool
def get_current_weather(city:str)->dict:
    """ this funciton can be used to get current weather information
    arguments:
        - city: name of city to get data for e.g. delhi, new york
    returns: JSON with wearher information
    
    """
    api_key="6a8b0ac166a37e2b7a38e64416b3c3fe"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    response = json.loads(response.content.decode())
    output = {"city":city,"weather":response['weather'][0]['description'],
              "temperature":response['main']['temp'], "unit":"kelvin"
              }
    return output

get_current_weather_tool= FunctionTool(get_current_weather)


# Langchain tool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

def wikipedia_tool(query:str):
    "this function accepts query to search on wikipedia and returns results, it can be used search about people, places, locations, events etc."
    op = wikipedia.run(query)
    return op

wiki_tool = FunctionTool(wikipedia_tool)


prompt = """
you are an expert assistant to human users who can provide correct information, based on internet search results to the users.
you are provided with multiple tools
You can use appropriate tool for the specific use case based on user query.
get current weather tool can be used to fetch current realtime weather information for any city, you need to mention only city name in small case.
wiki tool can be used to fetch information from wikipedia about people, places, events, the input query should be short and specific.

"""

root_agent = LlmAgent(name="TredenceAgent",
                      model="gemini-2.0-flash",
                      instruction=prompt,
                      description="Assitant Agent",
                      tools=[get_current_weather_tool,wiki_tool],)

