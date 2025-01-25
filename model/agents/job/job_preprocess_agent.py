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
    ral: int = Field(description="Gross annual RAL in euros. 0 if not present.")
    net_monthly: float = Field(description="Monthly net salary in euros, if any. 0 otherwise.")
    confidence: float = Field(description="Extraction confidence from 0 to 1")


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
        prefix = """Analyze the following job advertisement and extract the salary information.
        If the RAL (Gross Annual Salary) is present, extract it directly.
        If there is a range (example: "25,000-30,000€"), return the average between the various values
        If only the monthly net salary is present, report it and extract the value.
        If there is no salary information, return 0 as RAL.
        
        The result must be in JSON format with the fields: ral, net_monthly, trust

        Here some examples:"""

        suffix = """Announce: {job_posting}

        Output must be a JSON:"""

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