from typing import Tuple, Dict, Any

from langchain.agents import initialize_agent, AgentType
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.output_parsers import CommaSeparatedListOutputParser, StrOutputParser, PydanticOutputParser
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel, RunnableLambda
from langchain_core.tools import Tool
from langchain_ollama import OllamaLLM
from pydantic import BaseModel, Field

from prompts import skills_prompt, check_category_prompt, hard_skill_match, soft_skill_match
from tools import calcola_ral_da_netto


class RALOutput(BaseModel):
    ral: int = Field(description="RAL annuale lorda in euro. 0 se non presente.")
    net_monthly: float = Field(description="Stipendio netto mensile in euro, se presente. 0 altrimenti.")
    confidence: float = Field(description="Confidenza dell'estrazione da 0 a 1")

def job_preprocess_agent() -> Runnable:

    # Inizializzazione del modello
    llm = OllamaLLM(model = "gemma2", temperature = 0)

    # Chain per l'estrazione delle skill
    skills_chain = skills_prompt | llm

    # Parser per l'output strutturato
    parser = PydanticOutputParser(pydantic_object=RALOutput)

    # parser = JsonOutputParser()

    examples = [
        {
            "job_posting": """Cerchiamo sviluppatore Java senior. RAL 45.000€ - 55.000€ in base all'esperienza.""",
            "output": """{{"ral": 50000, "net_monthly": 0, "confidence": 0.95}}"""
        },
        {
            "job_posting": """Offriamo stipendio netto mensile di 2.200€ su 13 mensilità""",
            "output": """{{"ral": 0, "net_monthly": 2200, "confidence": 0.9}}"""
        },
        {
            "job_posting": """La nostra azienda offre un ambiente stimolante e benefit aziendali""",
            "output": """{{"ral": 0, "net_monthly": 0, "confidence": 1.0}}"""
        }
    ]

    # Template per ogni esempio
    example_template = """Annuncio: {job_posting}\nOutput: {output}"""

    # example_prompt = PromptTemplate.from_template(example_template)

    example_prompt = PromptTemplate(
        input_variables=["job_posting", "output"],
        template=example_template
    )

    # Template principale
    prefix = """Analizza il seguente annuncio di lavoro ed estrai le informazioni relative alla retribuzione.
    Se è presente la RAL (Retribuzione Annua Lorda), estraila direttamente.
    Se è presente un range (esempio: "25.000-30.000€"), restituisci la media tra i vari valori
    Se è presente solo lo stipendio netto mensile, segnalalo e estrai il valore.
    Se non sono presenti informazioni sulla retribuzione, ritorna 0 come RAL.
    
    Il risultato deve essere in formato JSON con i campi: ral, net_monthly, confidence

    Ecco alcuni esempi:"""

    suffix = """Annuncio: {job_posting}

    Output in formato JSON:"""

    # Creazione del few-shot prompt template
    few_shot_prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix=suffix,
        input_variables=["job_posting"],
        example_separator="\n\n"
    )

    def process_extraction(output: RALOutput) -> Dict[str, int]:
        """Processa l'output dell'estrazione e applica la logica di business"""
        if output.ral > 0:
            return {"ral": output.ral}
        elif output.net_monthly > 0:
            return {"needs_conversion": True, "net_monthly": output.net_monthly}
        else:
            return {"ral": 0}

    ral_chain = (
            few_shot_prompt
            | llm
            | parser
            | RunnableLambda(process_extraction)
            | (lambda x: calcola_ral_da_netto(x["net_monthly"]) if x.get("needs_conversion") else x["ral"])
    )

    return RunnableParallel(skills = skills_chain, ral = ral_chain)

def check_category_agent() -> Runnable:
    llm = OllamaLLM(model = "gemma2", temperature = 0)

    parser = StrOutputParser()
    return check_category_prompt | llm | parser | (lambda x: x.strip().lower() == "true")

def hard_skill_match_agent() -> Runnable:

    # Output parser per la lista separata da virgole
    output_parser = CommaSeparatedListOutputParser()

    llm = OllamaLLM(model = "gemma2", temperature = 0)

    return hard_skill_match | llm | output_parser


def check_company_agent() -> Runnable:
    search_tool = DuckDuckGoSearchResults()

    search_tool_revenue = DuckDuckGoSearchResults(output_format="json")

    llm = OllamaLLM(model="gemma2", temperature=0)

    def nation_headquarters(company_name):
        query = f"Semplicemente rispondi con il nome della nazione della sede legale di {company_name}, senza alcun altro testo."
        return search_tool.invoke(query)

    def company_revenue(company_name):
        query = f"Semplicemente rispondi il più recente fatturato disponibile di {company_name}, senza alcun altro testo."
        return search_tool_revenue.invoke(query)

    def company_sectors(company_name):
        sectors = [
            "Agricoltura, Industria e Ambiente",
            "Tecnologia e Innovazione",
            "Commercio, Logistica e Turismo",
            "Finanza e Servizi Legali",
            "Sanità e Benessere",
            "Educazione e Cultura",
            "Pubblica Amministrazione e No Profit"
        ]
        query = f"Verifica in quale dei seguenti settori opera {company_name}: {', '.join(sectors)}"
        response = search_tool.invoke(query)

        # Filtra i settori che compaiono nella risposta
        matching_sectors = [sector for sector in sectors if sector.lower() in response.lower()]
        return ', '.join(matching_sectors)

    # Inizializzazione dell'agente per ogni tool
    agent_nation = initialize_agent(
        llm= llm,
        tools=[Tool(name="headquarter_nation", func=nation_headquarters,
                    description="Trova la nazione della sede legale")],
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    agent_revenue = initialize_agent(
        llm=llm,
        tools=[Tool(name="company_revenue", func=company_revenue,
                    description="Trova il fatturato dell'azienda nello scorso anno")],
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    agent_sectors = initialize_agent(
        llm=llm,
        tools=[Tool(name="company_sectors", func=company_sectors,
                    description="Verifica i settori in cui opera l'azienda")],
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )

    # Combinazione con RunnableParallel
    return RunnableParallel(nation = agent_nation, revenue = agent_revenue, sectors = agent_sectors)




def soft_skill_match_agent() -> Runnable:

    # Output parser per la lista separata da virgole
    output_parser = CommaSeparatedListOutputParser()

    llm = OllamaLLM(model = "gemma2", temperature = 0)
    #llm = ChatOpenAI(temperature=0.)

    return soft_skill_match | llm | output_parser
