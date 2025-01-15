from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.tools import Tool
from pydantic import BaseModel

from model.agents.abstract.abstract_agent import AbstractAgent
from pydantic_extra_types.country import CountryAlpha3


class CompanySectorAgent(AbstractAgent):
    def __init__(self, **kwargs):
        self.search = DuckDuckGoSearchResults(backend='auto')
        self.sector_extractor_agent = SectorExtractorAgent()
        super().__init__(**kwargs)

    def extract_sector(self, text):
        return self.sector_extractor_agent.invoke({'text': text})


    def make_runnable(self, **kwargs) -> Runnable:
        """
        Funzione principale per cercare la nazione della sede legale di un'azienda
        """

        # Crea il tool per l'agente
        tools = [
            Tool(
                name="DuckDuckGo Search",
                func=self.search.run,
                description="Utile per cercare informazioni su un'azienda, in particolare di cosa si occupa"
            ),
            Tool(
                name="Sector Extractor",
                func=self.extract_sector,
                description="Utile per estrapolare il nome del settore in cui opera un azienda da un testo informativo"
            )
        ]


        # Inizializza l'agente
        agent = initialize_agent(
            tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False
        )

        starting_prompt = PromptTemplate.from_template("Restituisci SOLO il nome del settore in cui opera l'azienda {company_name}. Usa la query: What does the company {company_name} do? What sector does it operate in?")

        return starting_prompt | agent


class SectorExtractorAgent(AbstractAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make_runnable(self, **kwargs) -> Runnable:
        # Esempi Few-Shot
        examples = [
            {
                "text": """La nostra azienda si occupa di sviluppo software e soluzioni di cybersecurity.""",
                "output": """{{"code": "Tecnologia e Innovazione"}}"""
            },
            {
                "text": """L'impresa è specializzata nella produzione di alimenti biologici e nella gestione ambientale sostenibile.""",
                "output": """{{"code": "Agricoltura, Industria e Ambiente"}}"""
            },
            {
                "text": """L'attività principale della società riguarda il turismo e la gestione di strutture alberghiere.""",
                "output": """{{"code": "Commercio, Logistica e Turismo"}}"""
            },
            {
                "text": """L'azienda opera nel settore delle banche e dei servizi finanziari.""",
                "output": """{{"code": "Finanza e Servizi Legali"}}"""
            },
            {
                "text": """Non è chiaro a quale settore operativo appartenga l'organizzazione.""",
                "output": """{{"code": "N/A"}}"""
            }
        ]

        example_prompt = PromptTemplate(
            input_variables=["text", "output"],
            template="""Testo: {text}\nOutput: {output}\n"""
        )

        prefix = """
        
        Analizza il seguente testo e restituisci il settore in cui opera l'azienda.
        Il settore in cui opera l'azienda potrà essere SOLO uno di quelli presenti nella seguente lista:
        
            - **Agricoltura, Industria e Ambiente** (Agricoltura, allevamento, e alimentazione, Produzione industriale e manifatturiera, Energie rinnovabili e gestione ambientale)
            - **Tecnologia e Innovazione** ( IT, sviluppo software e telecomunicazioni,  Intelligenza artificiale, data science e cybersecurity)
            - **Commercio, Logistica e Turismo** (Vendita al dettaglio, e-commerce e distribuzione, Logistica e supply chain, Turismo, ospitalità e ristorazione)
            - **Finanza e Servizi Legali** (Servizi finanziari, banche e assicurazioni, Consulenza legale e protezione dei dati)
            - **Sanità e Benessere** (Medicina, farmaceutica e assistenza sanitaria, Sport, fitness e benessere)
            - **Educazione e Cultura** (Insegnamento, formazione e ricerca, Arte, cultura, media e intrattenimento)
            - **Pubblica Amministrazione e No Profit** (Organizzazioni governative, ONG e volontariato, Servizi pubblici e forze dell'ordine)
            
        Se non corrisponde a nessuno di questi settori, semplicemente rispondi N/A.
        Il risultato può consistere SOLO un uno dei settori elencati sopra oppure N/A.
        
        Di seguito alcuni esempi:

        """

        # Creazione del prompt Few-Shot
        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix=prefix,
            suffix="Testo: {text}\n\nIl tuo output:",
            input_variables=["text"],
            example_separator="\n\n",
        )

        return few_shot_prompt | self.llm
