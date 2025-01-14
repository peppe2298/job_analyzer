from typing import Dict

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, RunnableParallel
from pydantic import BaseModel, Field

from model.agents.abstract.abstract_agent import AbstractAgent
from model.prompts import skills_prompt
from service.ral_service import RalService


class JobPreprocessAgent(AbstractAgent):

    def __init__(self, **kwargs):
        self.ral_chain = RalExtractorAgent().runnable
        self.skills_chain = SkillSummarizerAgent().runnable
        super().__init__(**kwargs)

    def make_runnable(self, **kwargs) -> Runnable:
        return RunnableParallel(skills = self.skills_chain, ral = self.ral_chain)


class SkillSummarizerAgent(AbstractAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make_runnable(self, **kwargs) -> Runnable:
        return skills_prompt | self.llm


class RALOutput(BaseModel):
    ral: int = Field(description="RAL annuale lorda in euro. 0 se non presente.")
    net_monthly: float = Field(description="Stipendio netto mensile in euro, se presente. 0 altrimenti.")
    confidence: float = Field(description="Confidenza dell'estrazione da 0 a 1")


class RalExtractorAgent(AbstractAgent):

    def __init__(self, **kwargs):
        self.parser = PydanticOutputParser(pydantic_object=RALOutput)
        super().__init__(**kwargs)


    def process_extraction(self, output: RALOutput) -> Dict[str, int]:
        """Processa l'output dell'estrazione e applica la logica di business"""
        if output.ral > 0:
            return {"ral": output.ral}
        elif output.net_monthly > 0:
            return {"needs_conversion": True, "net_monthly": output.net_monthly}
        else:
            return {"ral": 0}

    def make_runnable(self, **kwargs) -> Runnable:

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

        return (
                few_shot_prompt
                | self.llm
                | self.parser
                | RunnableLambda(self.process_extraction)
                | (lambda x: RalService.get_ral_from_monthly_net(x["net_monthly"]) if x.get("needs_conversion") else x["ral"])
        )