from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import Tool
from pydantic import BaseModel, Field

from model.agents.abstract.abstract_agent import AbstractAgent
from service.currency_service import CurrencyService

class Revenue(BaseModel):
    value: int = Field(description='The amount of the company revenue, 0 if not present')

class CompanyRevenueAgent(AbstractAgent):
    def __init__(self, **kwargs):
        self.search = DuckDuckGoSearchResults(backend='auto')
        self.revenue_extractor_agent = RevenueExtractorAgent()
        self.currency_converter = CurrencyService
        self.parser  = PydanticOutputParser(pydantic_object=Revenue)
        super().__init__(**kwargs)

    def extract_revenue(self, text):
        return self.revenue_extractor_agent.invoke({'text': text})

    def make_runnable(self, **kwargs) -> Runnable:
        """
            Funzione principale per cercare il fatturato di un'azienda
            """

        # Crea il tool per l'agente
        tools = [
            Tool(
                name="DuckDuckGo Search",
                func=self.search.run,
                description="Useful for searching for text containing information on a company's turnover"
            ),
            Tool(
                name="Revenue Extractor",
                func=self.extract_revenue,
                description="Useful for extrapolating the exact value of a company's turnover from a text and passing it in JSON format"
            ),
            Tool(
                name="ConvertToEuro",
                description="Given a JSON, converts a currency amount (for example '1000000 USD') to euros if necessary and always returns an integer",
                func=self.currency_converter.convert
            )
        ]


        # Inizializza l'agente
        agent = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            handle_parsing_errors=True,
            parser=self.parser
        )

        starting_prompt = PromptTemplate.from_template("""Return ONLY the revenue of the company {company_name} in euros as an integer. 
        
        Use the query: How much is the most recent global turnover of the company {company_name}?
        
        If you can't find out the company's revenue, just return 0.
        
        """)

        return starting_prompt | agent


class RevenueExtractorAgent(AbstractAgent):

    def __init__(self, **kwargs):
        self.parser = JsonOutputParser()
        super().__init__(**kwargs)

    def make_runnable(self, **kwargs) -> Runnable:
        # Esempi Few-Shot
        examples = [
            {
                "text": """L'azienda ha registrato un fatturato di 2.500.000 euro nel 2022.""",
                "output": """{{"revenue": 2500000, "currency": "EUR"}}"""
            },
            {
                "text": """Nel 2021, il fatturato è stato di 3 milioni di dollari.""",
                "output": """{{"revenue": 3000000, "currency": "USD"}}"""
            },
            {
                "text": """Il fatturato annuale più recente è stato pari a 1.200.000 yen nel 2023.""",
                "output": """{{"revenue": 1200000, "currency": "JPY"}}"""
            },
            {
                "text": """Non ci sono informazioni sul fatturato nel testo.""",
                "output": """{{"revenue": 0, "currency": "N/A"}}"""
            }
        ]

        example_prompt = PromptTemplate(
            input_variables=["text", "output"],
            template="""Testo: {text}\nOutput: {output}\n"""
        )

        # Creazione del prompt Few-Shot
        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="Parse the following text and return the company's most recent annual revenue and associated currency.\n"
                   "If you don't find clear revenue, return 0 for revenue and 'N/A' for currency.\n"
                   "The currency must conform to ISO 4217 or 'N/A' format.\n Here are some examples:\n\n",
            suffix="Text: {text}\n\nYour output must be a JSON",
            input_variables=["text"],
            example_separator="\n\n",
        )

        return few_shot_prompt | self.llm | self.parser
