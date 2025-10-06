
from mcp.server.fastmcp import FastMCP
import requests, json
import wikipedia

mcp = FastMCP("TredenceMCP")

@mcp.tool()
async def get_current_weather(city:str)->dict:
    """ this funciton can be used to get current weather information"""
    api_key="6a8b0ac166a37e2b7a38e64416b3c3fe"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    response = json.loads(response.content.decode())
    output = {"city":city,"weather":response['weather'][0]['description'],
              "temperature":response['main']['temp'], "unit":"kelvin"
              }
    return output

@mcp.tool()
async def get_wikipedia_summary(query:str)->str:
    response = wikipedia.summary(query)
    return response


if __name__=="__main__":
    mcp.run(transport='streamable-http')
