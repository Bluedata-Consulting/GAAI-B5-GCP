from google.adk.agents import LlmAgent
from google.adk.tools import google_search

root_agent = LlmAgent(name="TredenceAgent",
                      model="gemini-2.0-flash",
                      instruction="you are an expert assistant to human users who can provide correct information, based on internet search results to the users.",
                      description="Assitant Agent",
                      tools=[google_search])

