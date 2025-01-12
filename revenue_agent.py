import ast

import requests
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.tools import DuckDuckGoSearchResults
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from langchain_core.prompt_values import StringPromptValue
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_ollama import OllamaLLM

from pydantic import Field, BaseModel
from pydantic.v1 import validator


# Elenco delle principali valute ISO 4217 con inclusione di "N/A"
VALID_CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD",
    "MXN", "SGD", "HKD", "NOK", "KRW", "TRY", "INR", "RUB", "BRL", "ZAR", "N/A"
]

# Modello Pydantic per il parsing dell'output
# NON USATO
class RevenueOutput(BaseModel):
    revenue: int = Field(description="Il fatturato annuale più recente dell'azienda, un numero intero positivo. Se non presente, 0.")
    currency: str = Field(description="La valuta associata al fatturato. Deve essere un codice ISO 4217 valido o 'N/A' se non applicabile.")

    # Validazione per il campo 'revenue'
    @validator("revenue")
    def must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Il fatturato deve essere un numero intero positivo o zero.")
        return v

    # Validazione per il campo 'currency'
    @validator("currency")
    def must_be_valid_currency(cls, v):
        if v not in VALID_CURRENCIES:
            raise ValueError(f"'{v}' non è una valuta valida. Usa un codice ISO 4217 o 'N/A'.")
        return v

def extract_revenue(text):
    """
    Funzione per estrarre il fatturato dal testo utilizzando LangChain.
    """
    # Inizializzazione del modello LLM
    llm = OllamaLLM(model="gemma2", temperature=0)

    # Creazione del parser
    # output_parser = PydanticOutputParser(pydantic_object=RevenueOutput)
    output_parser = JsonOutputParser()

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
        prefix= "Analizza il seguente testo e restituisci il fatturato annuale più recente dell'azienda e la valuta associata.\n"
               "Se non trovi un fatturato chiaro, restituisci 0 per il fatturato e 'N/A' per la valuta.\n"
               "La valuta deve essere conforme al formato ISO 4217 o 'N/A'.\n Di seguito alcuni esempi:\n\n",
        suffix="Testo: {text}\n\nIl tuo output deve essereJSON",
        input_variables=["text"],
        example_separator="\n\n",
    )

    chain = (few_shot_prompt |
             llm |
             output_parser)


    # Restituzione del fatturato come intero, o 0 se non presente
    try:
        return chain.invoke(input={'text':text})
    except Exception as e:
        print(f"Errore nel parsing: {e}")
        return 0, "N/A"

def convert_to_euro(amount_with_currency):
    # Parsing del valore e della valuta
    # amount, currency = amount_with_currency.split()
    dict_amount_with_currency = ast.literal_eval(amount_with_currency)
    amount = float(dict_amount_with_currency.get('revenue', 0))
    currency = dict_amount_with_currency.get('currency', 'N/A')
    if currency == 'N/A':
        return 0
    if currency == "EUR":
        return int(amount)  # Nessuna conversione necessaria
    # Chiamata all'API di conversione valutaria
    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}")
    data = response.json()
    exchange_rate = data["rates"]["EUR"]
    return int(amount * exchange_rate)

def search_company_revenue(company_name: str) -> int:
    """
    Funzione principale per cercare il fatturato di un'azienda
    """
    # Inizializza il tool di ricerca
    search = DuckDuckGoSearchResults()

    # Crea il tool per l'agente
    tools = [
        Tool(
            name="DuckDuckGo Search",
            func=search.run,
            description="Utile per cercare informazioni sul fatturato di un'azienda"
        ),
        Tool(
            name="Revenue Extractor",
            func=extract_revenue,
            description="Utile per estrapolare il valore esatto del fatturato di un azienda da un testo e passarlo in formato RevenueOutput"
        ),
        Tool(
            name="ConvertToEuro",
            description="Dato un RevenueOutput, converte un importo con valuta (ad esempio '1000000 USD') in euro.",
            func=convert_to_euro
        )
    ]

    # Inizializza l'LLM
    llm = OllamaLLM(model="gemma2", temperature=0)

    # Inizializza l'agente
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=False
    )

    # Query di ricerca
    search_query = f"How much is the most recent global turnover of the company {company}?"

    try:
        # Esegui la ricerca
        search_result = agent.run(f"Restituisci SOLO il fatturato dell'azienda {company_name} in euro. Usa la query: {search_query}")
        return search_result

        # Estrai il fatturato dal risultato
        # final_revenue = extract_revenue(search_result)
        # return final_revenue

    except Exception as e:
        print(f"Errore durante la ricerca: {e}")
        return 0


# Esempio di utilizzo
if __name__ == "__main__":
    company = "Deloitte"
    revenue = search_company_revenue(company)
    print(f"Il fatturato di {company} è: {revenue} €")