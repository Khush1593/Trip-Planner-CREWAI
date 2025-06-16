from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model = "ollama/llama3.2",
    base_url = "http://localhost:11434/v1",
)

@CrewBase
class PlannerCrew:
    """Planner Crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def trip_planner(self) -> Agent:
        return Agent(
			config=self.agents_config['trip_planner'],
			verbose=True,
			# allow_delegation=True,
			llm = llm
		)

    @task
    def planning_trip(self) -> Task:
        return Task(
			config=self.tasks_config['trip_plan_task'],
			output_file='report.md'
		)

    @crew
    def crew(self) -> Crew:
        """Creates the Research Crew"""

        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
    
