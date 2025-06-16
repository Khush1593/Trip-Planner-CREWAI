from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from src.trip_planner_flow.tools.google_search_tool import MyCustomTool
from src.trip_planner_flow.tools.map_search_tool import MapSearchTool
from crewai_tools import ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="ollama/llama3.2",
    base_url = "http://localhost:11434/v1",
)

@CrewBase
class PlaceCrew:
    """Place Crew"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def city_selector(self) -> Agent:
        return Agent(
			config=self.agents_config['city_selector'],
			tools=[MyCustomTool(), MapSearchTool()], # Example of custom tool, loaded on the beginning of file
			verbose=True,
			max_iter = 10,
			# allow_delegation=True,
			llm = llm
		)

    @task
    def write_poem(self) -> Task:
        return Task(
			config=self.tasks_config['city_selection_task'],
		)

    @crew
    def crew(self) -> Crew:
        """Creates the Trip planner Crew"""

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )