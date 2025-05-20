# plot_consistency_checker.py
from langgraph.agents import Agent
from src.prompts.prompts import PLOT_CONSISTENCY_PROMPT
from src.config.settings import settings
from src.utils.helpers import get_llm
class PlotConsistencyChecker:
    def __init__(self):
        self.agent = Agent(prompt=PLOT_CONSISTENCY_PROMPT, llm=get_llm(settings.LLM_MODEL))

    def check_consistency(self, plot: str) -> bool:
        return self.agent.invoke(plot)

plot_consistency_checker = PlotConsistencyChecker()

if __name__ == "__main__":
    plot_consistency_checker.check_consistency("This is a plot outline.")
