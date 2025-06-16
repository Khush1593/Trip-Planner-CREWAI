from typing import Type
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
import requests, json, os

class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    query: str = Field(..., description="The Query that helps in finding the hotels related details using Maps.")

class MapSearchTool(BaseTool):
    name: str = "Search Maps"
    description: str = (
        "For Answering the query this tool helps to search over the Maps and get the details for hotels."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, query: str) -> str:
        # the way we can call a request (default by serper)
        top_result_to_return = 4
        url = "https://google.serper.dev/maps"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        
        # check if there is an organic key
        if 'organic' not in response.json():
            return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
        else:
            results = response.json()['organic']
            string = []
            for result in results[:top_result_to_return]:
                try:
                    string.append('\n'.join([
                        f"Title: {result['title']}", f"Link: {result['link']}",
                        f"Snippet: {result['snippet']}", "\n-----------------"
                    ]))
                except KeyError:
                    next

            return '\n'.join(string)