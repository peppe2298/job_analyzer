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
                description="Utile per cercare informazioni sul sulla nazione della sede legale di un'azienda"
            ),
            Tool(
                name="Country Extractor",
                func=self.extract_country,
                description="Utile per estrapolare il paese esatto in formato 'ISO 3166-1 alpha-3' della sede legale di un azienda da un testo"
            )
        ]


        # Inizializza l'agente
        agent = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )

        starting_prompt = PromptTemplate.from_template("Restituisci SOLO il codice 'ISO 3166-1 alpha-3' della nazione dell'azienda {company_name}. Usa la query: Where is the country of the registered office of the company {company_name} located?")

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

        # Creazione del prompt Few-Shot
        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="Analizza il seguente testo e restituisci la nazione della sede legale dell'azienda nel formato 'ISO 3166-1 alpha-3'.\n"
                   "Se la nazione è scritta per esteso o in altri modi, convertila nel formato 'ISO 3166-1 alpha-3'.\n"
                   "il risultato può consistere SOLO nel codice della nazione trovata convertito nel formato 'ISO 3166-1 alpha-3' oppure 'N/A'.\n Di seguito alcuni esempi:\n\n",
            suffix="Testo: {text}\n\nIl tuo output deve essere JSON",
            input_variables=["text"],
            example_separator="\n\n",
        )

        return few_shot_prompt | self.llm | self.parser
