from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import Tool
from pydantic import BaseModel

from model.agents.abstract.abstract_agent import AbstractAgent
from pydantic_extra_types.country import CountryAlpha3

class Country(BaseModel):
    code: CountryAlpha3

class CompanyHeadquarterCountryAgent(AbstractAgent):
    def __init__(self, **kwargs):
        self.search = DuckDuckGoSearchResults(backend='auto')
        self.headquarter_country_extractor_agent = CountryExtractorAgent()
        super().__init__(**kwargs)

    def extract_country(self, text):
        try:
            country: Country = self.headquarter_country_extractor_agent.invoke({'text': text})
            return country.code
        except Exception as e:
            print(e)
            print(f'nazione non trovata in {text}\n')
            return 'N/A'

    def make_runnable(self, **kwargs) -> Runnable:
        """
            Funzione principale per cercare la nazione della sede legale di un'azienda
            """

        # Crea il tool per l'agente
        tools = [
            Tool(
                name="DuckDuckGo Search",
                func=self.search.run,
                description="Useful for searching for information on the country of a company's registered office"
            ),
            Tool(
                name="Country Extractor",
                func=self.extract_country,
                description="Useful for extracting the exact country in 'ISO 3166-1 alpha-3' format of a company's registered office from a text"
            )
        ]


        # Inizializza l'agente
        agent = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )

        starting_prompt = PromptTemplate.from_template("Return ONLY the 'ISO 3166-1 alpha-3' country code of the company {company_name}. Use the query: Where is the country of the registered office of the company {company_name} located?")

        return starting_prompt | agent


class CountryExtractorAgent(AbstractAgent):

    def __init__(self, **kwargs):
        self.parser = PydanticOutputParser(pydantic_object=Country)
        super().__init__(**kwargs)

    def make_runnable(self, **kwargs) -> Runnable:
        # Esempi Few-Shot
        examples = [
            {
                "text": """Canada.""",
                "output": """{{"code": "CAN"}}"""
            },
            {
                "text": """Regno Unito.""",
                "output": """{{"code": "GBR"}}"""
            },
            {
                "text": """La sede legale dell'azienda si trova in Italia.""",
                "output": """{{"code": "ITA"}}"""
            },
            {
                "text": """Non ci sono informazioni sulla sede legale nel testo.""",
                "output": """{{"code": "N/A"}}"""
            },
        ]

        example_prompt = PromptTemplate(
            input_variables=["text", "output"],
            template="""Testo: {text}\nOutput: {output}\n"""
        )

        prefix = """
                    Parse the following text and return the country of the registered office of the company in 'ISO 3166-1 alpha-3' format.
                    
                    If the country is written out or otherwise, convert it to 'ISO 3166-1 alpha-3' format.
                    
                    The result can be ONLY the code of the found country converted to 'ISO 3166-1 alpha-3' format or 'N/A'.
                    
                    Here are some examples:
                    
                    """

        # Creazione del prompt Few-Shot
        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix=prefix,
            suffix="Text: {text}\n\nYour output must be a JSON",
            input_variables=["text"],
            example_separator="\n\n",
        )

        return few_shot_prompt | self.llm | self.parser
