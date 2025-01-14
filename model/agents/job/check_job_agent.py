from langchain_core.output_parsers import BaseOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable

from model.agents.abstract.abstract_agent import AbstractAgent

class CheckSkillAgent(AbstractAgent):

    def __init__(self, prompt: PromptTemplate, **kwargs):
        self.prompt: PromptTemplate = prompt
        self.parser: BaseOutputParser = StrOutputParser()
        super().__init__(**kwargs)


    def make_runnable(self, **kwargs) -> Runnable:
        return self.prompt | self.llm | self.parser

class CheckCategoryAgent(AbstractAgent):

    def __init__(self, prompt: PromptTemplate, **kwargs):
        self.prompt: PromptTemplate = prompt
        self.parser: BaseOutputParser = StrOutputParser()
        super().__init__(**kwargs)

    def make_runnable(self, **kwargs) -> Runnable:
        return self.prompt | self.llm | self.parser | (lambda x: x.strip().lower() == "true")