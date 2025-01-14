from langchain_core.runnables import Runnable, RunnableParallel

from model.agents.abstract.abstract_agent import AbstractAgent
from model.agents.company.company_revenue_agent import CompanyRevenueAgent


class CompanyAgent(AbstractAgent):

    def __init__(self, **kwargs):
        self.revenue_agent = CompanyRevenueAgent()
        super().__init__(**kwargs)

    def make_runnable(self) -> Runnable:
        # return RunnableParallel(nation=agent_nation, revenue=agent_revenue.runnable(), sectors=agent_sectors)
        return RunnableParallel(revenue=self.revenue_agent.runnable)