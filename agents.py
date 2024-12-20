from typing import Tuple

from langchain_core.output_parsers import CommaSeparatedListOutputParser, BaseOutputParser
from langchain_core.runnables import Runnable, RunnableParallel
from langchain_ollama import OllamaLLM

from prompts import contract_level_prompt, skills_prompt, check_category_prompt, hard_skill_match, soft_skill_match, \
    ral_prompt


def job_preprocess_agent() -> Runnable:

    # Inizializzazione del modello
    llm = OllamaLLM(model = "gemma2", temperature = 0)

    # Output parser per la lista separata da virgole
    output_parser = CommaSeparatedListOutputParser()

    # Chain per l'analisi del contratto e livello
    contract_level_chain = (
            contract_level_prompt
            | llm
            | output_parser
            | (lambda x: tuple(item.strip() for item in x))
    )

    # Chain per l'estrazione delle skill
    skills_chain = skills_prompt | llm

    integer_parser = IntegerOutputParser()

    ral_chain = ral_prompt | llm | integer_parser

    return RunnableParallel(contract_info = contract_level_chain, skills = skills_chain, ral = ral_chain)

def check_category_agent() -> Runnable:
    llm = OllamaLLM(model="gemma2", temperature=0)

    return check_category_prompt | llm | (lambda x: x.strip().lower() == "true")

def hard_skill_match_agent() -> Runnable:

    # Output parser per la lista separata da virgole
    output_parser = CommaSeparatedListOutputParser()

    llm = OllamaLLM(model="gemma2", temperature=0)

    return hard_skill_match | llm | output_parser


def soft_skill_match_agent() -> Runnable:

    # Output parser per la lista separata da virgole
    output_parser = CommaSeparatedListOutputParser()

    llm = OllamaLLM(model="gemma2", temperature=0)

    return soft_skill_match | llm | output_parser

class IntegerOutputParser(BaseOutputParser):
    def parse(self, text: str) -> int:
        try:
            # Rimuovi eventuali spazi o caratteri extra
            cleaned_text = text.strip()
            # Tenta di convertire l'output in un intero
            return int(cleaned_text)
        except ValueError:
            # Restituisci 0 se non è possibile convertire
            return 0

    def get_format_instructions(self) -> str:
        return "Assicurati che il risultato sia un numero intero."