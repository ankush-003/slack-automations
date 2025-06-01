from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crew.models import get_crew_llm
from crewai.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

@tool("Website Search Tool")
def website_search_tool(question: str) -> str:
    """Search the web for information on a given topic"""
    return DuckDuckGoSearchRun().invoke(question)

@CrewBase   
class SlackCrew:
    """Description of your crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml' 
    tasks_config = 'config/tasks.yaml' 

    @before_kickoff
    def prepare_inputs(self, inputs):
        return inputs

    @after_kickoff
    def process_output(self, output):
        return output

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            tools=[website_search_tool],
            llm=get_crew_llm(),
            verbose=True
        )

    @agent
    def slack_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['slack_reporter'], # type: ignore[index]
            verbose=True,
            llm=get_crew_llm()
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'] # type: ignore[index]
        )

    @task
    def slack_report_task(self) -> Task:
        return Task(
            config=self.tasks_config['slack_report_task'] # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  
            tasks=self.tasks,    
            process=Process.sequential,
            verbose=True,
        )

if __name__ == "__main__":
    # agent = Agent(
    #         role="researcher",
    #         goal="Research the topic",
    #         backstory="You are a researcher",
    #         tools=[website_search_tool],
    #         llm=get_crew_llm(),
    #         allow_delegation=True,
    #         verbose=True
    #     )
    
    # agent.kickoff(messages=[{'role': 'user', 'content': 'What is the capital of France?'}])

    crew = SlackCrew().crew()
    output = crew.kickoff(inputs={'question': input("Enter your question: ")})
    print(output.raw)
    