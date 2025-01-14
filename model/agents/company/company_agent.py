from langchain_core.runnables import Runnable, RunnableParallel

from model.agents.abstract.abstract_agent import AbstractAgent
from model.agents.company.company_headquarter_country_agent import CompanyHeadquarterCountryAgent
from model.agents.company.company_revenue_agent import CompanyRevenueAgent


class Company:
    country: str
    revenue: int

    def __init__(self, country: str, revenue: int):
        self.country = country
        self.revenue = revenue

class ProcessedCompanies:
    # Dizionario statico condiviso
    company_list: dict[str, Company] = {}

    @staticmethod
    def get_data():
        """Restituisce il dizionario condiviso."""
        return ProcessedCompanies.company_list

    @staticmethod
    def update_data(key, value):
        """Aggiorna il dizionario condiviso con una nuova chiave e valore."""
        ProcessedCompanies.company_list[key] = value

    @staticmethod
    def remove_data(key):
        """Rimuove un elemento dal dizionario condiviso."""
        if key in ProcessedCompanies.company_list:
            del ProcessedCompanies.company_list[key]

class CompanyAgent(AbstractAgent):

    _company_list = {}

    def __init__(self, **kwargs):
        self.revenue_agent = CompanyRevenueAgent()
        self.country_agent = CompanyHeadquarterCountryAgent()
        super().__init__(**kwargs)

    def make_runnable(self) -> Runnable:
        # return RunnableParallel(nation=agent_nation, revenue=agent_revenue.runnable(), sectors=agent_sectors)
        return RunnableParallel(country=self.country_agent.runnable, revenue=self.revenue_agent.runnable)